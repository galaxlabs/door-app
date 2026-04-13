from django.db import transaction
from django.utils import timezone

from apps.queue_control.models import Queue, QueueSession


class QueueService:
    @staticmethod
    @transaction.atomic
    def open_session(*, queue: Queue, actor=None) -> QueueSession:
        QueueSession.objects.filter(queue=queue, status="active").update(status="ended", ended_at=timezone.now())
        return QueueSession.objects.create(queue=queue, started_by=actor, status="active")

    @staticmethod
    def change_status(*, queue: Queue, status: str) -> Queue:
        queue.status = status
        queue.save(update_fields=["status"])
        return queue
