"""Celery application configured through Django settings."""

import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_asistant_with_sina.settings')

app = Celery('ai_asistant_with_sina')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
