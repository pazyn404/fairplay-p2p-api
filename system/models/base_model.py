import re
import inspect

from sqlalchemy import select

from db import Base
from config import VerificationError, ViolatedConstraintError
from utils import sign


class BaseModel(Base):
    __abstract__ = True

    def __init__(self, **kwargs):
        for column in self.__table__.columns:
            default = column.default
            if default is not None:
                if callable(default.arg):
                    kwargs[column.name] = default.arg()
                else:
                    kwargs[column.name] = default.arg

        super().__init__(**kwargs)

    def __init_subclass__(cls, **kwargs):
        if not cls.__dict__.get("__abstract__", False):
            table_name = re.sub(r"(?<!^)(?=[A-Z])", "_", cls.__name__)
            cls.__tablename__ = table_name.lower()

    @property
    def data(self):
        return self._parse_attrs(self.__class__.DATA_ATTRIBUTES)

    @property
    def user_signature_data(self):
        return self._parse_attrs(self.__class__.USER_SIGNATURE_ATTRIBUTES)

    @property
    def system_signature_data(self):
        return self._parse_attrs(self.__class__.SYSTEM_SIGNATURE_ATTRIBUTES)

    @property
    def system_signature(self):
        data = self.system_signature_data
        signature = sign(data)

        return signature

    def _options(self):
        return []

    async def fetch_related(self, session):
        query = select(self.__class__).filter_by(id=self.id).options(*self._options())
        await session.execute(query)

    def update(self, **kwargs):
        for attr, val in kwargs.items():
            setattr(self, attr, val)

    async def violated_constraints(self, session):
        errors = []
        for name, f in inspect.getmembers(self.__class__, predicate=inspect.isfunction):
            if name.startswith("violated_constraint_"):
                try:
                    await f(self, session)
                except ViolatedConstraintError as e:
                    errors.append(str(e))

        return errors

    def verify(self, prev_data=None):
        prev_data = prev_data or {}
        prev_data = {f"prev_{param}": val for param, val in prev_data.items()}
        response_status_code = None
        errors_by_status_code = {}
        for name, f in inspect.getmembers(self.__class__, predicate=inspect.isfunction):
            if name.startswith("verify_"):
                try:
                    params = list(inspect.signature(f).parameters)[1:]
                    selected_prev_data = {param: prev_data.get(param) for param in params}
                    f(self, **selected_prev_data)
                except VerificationError as e:
                    response_status_code = e.status_code if not response_status_code else min(response_status_code, e.status_code)
                    errors_by_status_code[e.status_code] = errors_by_status_code.get(e.status_code, set())
                    errors_by_status_code[e.status_code].add(str(e))

        errors = []
        for status_code in sorted(errors_by_status_code, reverse=True):
            for error in errors_by_status_code[status_code]:
                errors.append(error)

        return errors, response_status_code

    def update_related(self, prev_data=None):
        prev_data = prev_data or {}
        prev_data = {f"prev_{param}": val for param, val in prev_data.items()}
        for name, f in inspect.getmembers(self.__class__, predicate=inspect.isfunction):
            if name.startswith("update_related_"):
                params = list(inspect.signature(f).parameters)[1:]
                selected_prev_data = {param: prev_data.get(param) for param in params}
                f(self, **selected_prev_data)

    def _parse_attrs(self, attrs):
        def parse_attr(obj, attr):
            if "." not in attr:
                res = getattr(obj, attr)
                return res

            relation, attr = attr.split(".", maxsplit=1)
            val = getattr(obj, relation)
            if isinstance(val, list):
                return [
                    parse_attr(_val, attr) for _val in val
                ]

            return parse_attr(val, attr)

        data = {}
        for attr in attrs:
            if isinstance(attr, tuple):
                name, val = attr
                data[name] = val
            elif "|" in attr:
                name, attr = attr.split("|")
                data[name] = parse_attr(self, attr)
            else:
                data[attr] = parse_attr(self, attr)

        return data
