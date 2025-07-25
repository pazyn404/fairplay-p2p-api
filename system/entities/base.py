import inspect
from copy import deepcopy
from typing import Any

from exceptions import VerificationError, ViolatedConstraintError
from utils import sign


class BaseEntity:
    def __init__(self):
        self._prev_data = {}

    @property
    def data(self) -> dict:
        return self._parse_attrs(self.__class__.DATA_ATTRIBUTES)

    @property
    def user_signature_data(self) -> dict:
        return self._parse_attrs(self.__class__.USER_SIGNATURE_ATTRIBUTES)

    @property
    def system_signature_data(self) -> dict:
        return self._parse_attrs(self.__class__.SYSTEM_SIGNATURE_ATTRIBUTES)

    @property
    def system_signature(self) -> bytes:
        data = self.system_signature_data
        signature = sign(data)

        return signature

    def fill_from_related(self) -> None:
        raise NotImplementedError

    def store_prev_data(self):
        self._prev_data = {f"prev_{param}": deepcopy(val) for param, val in self.__dict__.items()}

    def update(self, **kwargs) -> None:
        for attr, val in kwargs.items():
            setattr(self, attr, val)

    def verify(self) -> list[VerificationError]:
        errors = []
        for name, f in inspect.getmembers(self.__class__, predicate=inspect.isfunction):
            if name.startswith("verify_"):
                try:
                    params = list(inspect.signature(f).parameters)[1:]
                    selected_prev_data = {param: self._prev_data.get(param) for param in params}
                    f(self, **selected_prev_data)
                except VerificationError as e:
                    errors.append(e)

        return errors

    def update_related(self) -> None:
        for name, f in inspect.getmembers(self.__class__, predicate=inspect.isfunction):
            if name.startswith("update_related_"):
                params = list(inspect.signature(f).parameters)[1:]
                selected_prev_data = {param: self._prev_data.get(param) for param in params}
                f(self, **selected_prev_data)

    def _parse_attrs(self, attrs: list[str]) -> dict:
        def parse_attr(obj: Any, attr: str) -> Any:
            if "." not in attr:
                res = getattr(obj, attr)
                return res

            relation, attr = attr.split(".", maxsplit=1)
            val = getattr(obj, relation)
            if isinstance(val, list):
                return [parse_attr(_val, attr) for _val in val]

            return parse_attr(val, attr)

        data = {}
        for attr in attrs:
            if "|" in attr:
                name, attr = attr.split("|")
                data[name] = parse_attr(self, attr)
            else:
                data[attr] = parse_attr(self, attr)

        return data
