from os import environ


class AppConfig:
    SECRET_KEY = environ["SECRET_KEY"]
    SQLALCHEMY_DATABASE_URI = environ["DATABASE_URI"]
    SQLALCHEMY_ENGINE_OPTIONS = {
        "isolation_level": "REPEATABLE READ"
    }
