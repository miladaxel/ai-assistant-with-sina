"""Submit persisted work only after the surrounding transaction commits."""

import logging

from django.db import transaction
from kombu.exceptions import KombuError
from redis.exceptions import RedisError

logger = logging.getLogger(__name__)


def enqueue_after_commit(task, record):
    model = type(record)
    record_id = record.pk

    def submit():
        try:
            task.apply_async(args=[record_id], retry=False)
        except (KombuError, RedisError, OSError):
            logger.exception('Could not enqueue %s %s', model.__name__, record_id)
            model.objects.filter(pk=record_id, status='pending').update(
                status='failure',
                error_message='ارسال درخواست انجام نشد. لطفاً چند لحظه بعد دوباره تلاش کنید.',
            )

    transaction.on_commit(submit)
