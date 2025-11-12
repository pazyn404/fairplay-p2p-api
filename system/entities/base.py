import inspect
from copy import deepcopy

from exceptions import VerificationError, VerificationErrorsList
from utils import sign


class BaseEntity:
    def __init__(self):
        self._prev_data = {}

    @property
    def user_signature_data(self) -> dict[str, int | str | None]:
        raise NotImplementedError

    @property
    def system_signature_data(self) -> dict[str, int | str | None]:
        raise NotImplementedError

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

    def verify(self) -> None:
        errors = []
        for name, f in inspect.getmembers(self.__class__, predicate=inspect.isfunction):
            if name.startswith("verify_"):
                try:
                    params = list(inspect.signature(f).parameters)[1:]
                    selected_prev_data = {param: self._prev_data.get(param) for param in params}
                    f(self, **selected_prev_data)
                except VerificationError as e:
                    errors.append(e)

        if errors:
            raise VerificationErrorsList(errors)

    def update_related(self) -> None:
        for name, f in inspect.getmembers(self.__class__, predicate=inspect.isfunction):
            if name.startswith("update_related_"):
                params = list(inspect.signature(f).parameters)[1:]
                selected_prev_data = {param: self._prev_data.get(param) for param in params}
                f(self, **selected_prev_data)
