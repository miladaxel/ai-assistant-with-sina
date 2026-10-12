"""Background tasks discovered by the project's Celery application."""

from celery import shared_task


@shared_task
def ping():
    """Verify that the broker, worker and result backend work end to end."""
    return 'pong'
