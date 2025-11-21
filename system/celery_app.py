from os import environ

from celery import Celery


celery_app = Celery(__name__)
celery_app.conf.update({
    "broker_url": environ["CELERY_BROKER_URL"],
    "include": [
        "celery_app_tasks"
    ],
    "task_acks_late": True,
    "task_visibility_timeout": 60
})
