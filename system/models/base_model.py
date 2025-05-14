import re
import inspect
from collections.abc import Coroutine

from db import Base
from config import VerificationError
from sqlalchemy import select
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
    def curr_data(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

    @property
    async def data(self):
        return await self._parse_attrs(self.__class__.DATA_ATTRIBUTES)

    @property
    async def user_signature_data(self):
        return await self._parse_attrs(self.__class__.USER_SIGNATURE_ATTRIBUTES)

    @property
    async def system_signature_data(self):
        return await self._parse_attrs(self.__class__.SYSTEM_SIGNATURE_ATTRIBUTES)

    @property
    async def system_signature(self):
        data = await self.system_signature_data
        signature = sign(data)

        return signature

    def update(self, **kwargs):
        for attr, val in kwargs.items():
            setattr(self, attr, val)

    async def verify(self, prev_data=None):
        prev_data = prev_data or {}
        prev_data = {f"prev_{param}": val for param, val in prev_data.items()}
        response_status_code = None
        errors_by_status_code = {}
        for name, f in inspect.getmembers(self.__class__, predicate=inspect.isfunction):
            if name.startswith("verify_"):
                try:
                    params = list(inspect.signature(f).parameters)[1:]
                    selected_prev_data = {param: prev_data.get(param) for param in params}
                    await f(self, **selected_prev_data)
                except VerificationError as e:
                    response_status_code = e.status_code if not response_status_code else min(response_status_code, e.status_code)
                    errors_by_status_code[e.status_code] = errors_by_status_code.get(e.status_code, set())
                    errors_by_status_code[e.status_code].add(str(e))

        errors = []
        for status_code in sorted(errors_by_status_code, reverse=True):
            for error in errors_by_status_code[status_code]:
                errors.append(error)

        return errors, response_status_code

    async def update_related(self, prev_data=None):
        prev_data = prev_data or {}
        prev_data = {f"prev_{param}": val for param, val in prev_data.items()}
        for name, f in inspect.getmembers(self.__class__, predicate=inspect.isfunction):
            if name.startswith("update_related_"):
                params = list(inspect.signature(f).parameters)[1:]
                selected_prev_data = {param: prev_data.get(param) for param in params}
                await f(self, **selected_prev_data)

    async def _parse_attrs(self, attrs):
        async def parse_attr(obj, attr):
            """
            used to parse relations for example:
            1) User:user_id.action_number
            get user by user_id of current instance then return action_number of found user if user does not exist return None
            2) {GAME_MODEL}:game_id.action_number
            the same as in 1) example, but GAME_MODEL will be get from instance as it's attribute(instance.GAME_MODEL)
            3) []{SYSTEM_ACTION_MODEL}:game_id:id.data
            the same as in previous examples but filter_by(game_id will be applied as filtered field filter_by(game_id=instance.id)) applied instead of get and return list
            4) {GAME_MODEL}.GAME_NAME
            return value of GAME_NAME attribute of instance.GAME_MODEL class
            """
            import models

            if "." not in attr:
                res = getattr(obj, attr)
                if isinstance(res, Coroutine):
                    return await res

                return res

            relation, attr = attr.split(".", maxsplit=1)

            if "{" in relation:
                model_attr = re.search(r"\{([^}]*)\}", relation).group(1)
                model = getattr(self.__class__, model_attr)
                relation = re.sub(r"\{([^}]*)\}", model.__name__, relation)

            if ":" not in relation:
                return await parse_attr(getattr(models, relation), attr)

            as_list = False
            if relation.startswith("[]"):
                relation = relation[2:]
                as_list = True

            if as_list:
                model_name, model_attr, obj_attr = relation.split(":")
                query = select(getattr(models, model_name)).filter_by(
                    **{model_attr: getattr(obj, obj_attr)}
                )
                res = await self.session.execute(query)
                instances = res.scalars().all()
                for instance in instances:
                    instance.session = self.session

                return [await parse_attr(instance, attr) for instance in instances]
            else:
                model_name, obj_attr = relation.split(":")
                instance = await self.session.get(getattr(models, model_name), getattr(obj, obj_attr))
                if not instance:
                    return None

                instance.session = self.session

                return await parse_attr(instance, attr)

        data = {}
        for attr in attrs:
            if isinstance(attr, tuple):
                name, val = attr
                data[name] = val
            elif "|" in attr:
                name, attr = attr.split("|")
                data[name] = await parse_attr(self, attr)
            else:
                data[attr] = await parse_attr(self, attr)

        return data
