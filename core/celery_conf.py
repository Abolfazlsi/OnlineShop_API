# celery_conf.py
import os
from celery import Celery
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.development')

celery_app = Celery('core')
celery_app.config_from_object('django.conf:settings', namespace='CELERY')
celery_app.autodiscover_tasks()

celery_app.conf.broker_url = "amqp://localhost"
celery_app.conf.result_backend = "rpc://"
celery_app.conf.timezone = "UTC"
celery_app.conf.task_serializer = "json"
celery_app.conf.result_serializer = "pickle"
celery_app.conf.accept_content = ["json", "pickle"]
celery_app.conf.result_expires = timedelta(days=1)
celery_app.conf.task_always_eager = False




