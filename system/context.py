from contextvars import ContextVar


entity_cache = ContextVar("entity_cache")
postgres_session = ContextVar("postgres_session")
