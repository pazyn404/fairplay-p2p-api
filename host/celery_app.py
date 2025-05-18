from celery import Celery

from config import CeleryAppConfig


celery_app = Celery(__name__)
celery_app.config_from_object(CeleryAppConfig)
