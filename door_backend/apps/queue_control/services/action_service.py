from django.db import transaction
from django.utils import timezone

from apps.queue_control.models import QueueActionLog, QueueTicket


class QueueActionService:
    @staticmethod
    @transaction.atomic
    def transition_ticket(*, ticket: QueueTicket, action: str, actor=None, actor_device_id: str = "") -> QueueTicket:
        before = {"status": ticket.status}
        mapping = {
            "call": "called",
            "skip": "skipped",
            "recall": "recalled",
            "complete": "completed",
            "cancel": "cancelled",
        }
        if action in mapping:
            ticket.status = mapping[action]
            if action == "call":
                ticket.called_at = timezone.now()
            if action == "recall":
                ticket.recalled_at = timezone.now()
            if action == "complete":
                ticket.completed_at = timezone.now()
            if action == "cancel":
                ticket.cancelled_at = timezone.now()
            ticket.save()

        QueueActionLog.objects.create(
            queue=ticket.queue,
            session=ticket.session,
            ticket=ticket,
            actor_user=actor,
            actor_device_id=actor_device_id,
            action=action,
            before_state=before,
            after_state={"status": ticket.status},
        )
        return ticket
