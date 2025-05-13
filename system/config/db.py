from os import environ


class DBConfig:
    DATABASE_URI = environ["DATABASE_URI"]
    SYNC_DATABASE_URI = environ["SYNC_DATABASE_URI"]