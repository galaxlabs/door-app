from django.db import transaction

from apps.queue_control.models import QueueSession, QueueTicket


class QueueTicketService:
    @staticmethod
    @transaction.atomic
    def issue_ticket(*, queue, session: QueueSession, user=None, device_id: str = "", scan_token=None):
        last = QueueTicket.objects.filter(session=session).order_by("-number").first()
        number = (last.number + 1) if last else 1
        return QueueTicket.objects.create(
            queue=queue,
            session=session,
            user=user,
            device_id=device_id,
            issued_from_scan_token=scan_token,
            number=number,
            status="issued",
        )
