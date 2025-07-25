from db import Base


class BaseModel(Base):
    __abstract__ = True

    def update(self, **kwargs) -> None:
        for k, v in kwargs.items():
            setattr(self, k, v)
