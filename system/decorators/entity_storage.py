from typing import Callable

from entities import BaseEntity
from context import entity_cache


def entity_storage(f: Callable) -> Callable:
    async def wrapper(*args, **kwargs) -> BaseEntity | list[BaseEntity] | None:
        res = await f(*args, **kwargs)
        _entity_cache = entity_cache.get(None)
        if _entity_cache is None:
            return res
        if res is None:
            return

        if isinstance(res, list):
            entities = []
            for entity in res:
                _entity_cache[entity.__class__.__name__] = _entity_cache.get(entity.__class__.__name__, {})
                _entity_cache[entity.__class__.__name__][entity.id] = _entity_cache[entity.__class__.__name__].get(entity.id, entity)
                entities.append(_entity_cache[entity.__class__.__name__][entity.id])

            return entities
        else:
            entity = res
            _entity_cache[entity.__class__.__name__] = _entity_cache.get(entity.__class__.__name__, {})
            _entity_cache[entity.__class__.__name__][entity.id] = _entity_cache[entity.__class__.__name__].get(entity.id, entity)

            return _entity_cache[entity.__class__.__name__][entity.id]

    return wrapper
