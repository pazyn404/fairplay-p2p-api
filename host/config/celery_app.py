from os import environ


class CeleryAppConfig:
    CELERY_BROKER_URL = environ["CELERY_BROKER_URL"]
    include = [
        "tasks.complete_game_on_timeout",
        "tasks.payout"
    ]
    task_acks_late = True
    task_visibility_timeout = 60
