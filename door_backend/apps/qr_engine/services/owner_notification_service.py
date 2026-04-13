from django.db import transaction
from django.utils import timezone

from apps.notifications.services.notification_service import NotificationService
from apps.qr_engine.models import QRScan, QRAlert, QROwnerMember, QRAlertRecipient


class QROwnerNotificationService:
    @staticmethod
    @transaction.atomic
    def trigger_alert_for_scan(*, scan: QRScan) -> QRAlert | None:
        members = list(
            QROwnerMember.objects.filter(
                qr_code=scan.qr_code,
                is_active=True,
            )
            .select_related("member_user")
            .order_by("priority", "created_at_server")
        )
        if not members:
            return None

        cc_ids = [str(m.id) for m in members if m.notify_role == "cc"]
        bcc_ids = [str(m.id) for m in members if m.notify_role == "bcc"]

        alert = QRAlert.objects.create(
            scan=scan,
            qr_code=scan.qr_code,
            triggered_by=scan.scanned_by,
            message=f"QR alert triggered for {scan.qr_code.label}",
            cc_snapshot=cc_ids,
            bcc_snapshot=bcc_ids,
            meta={
                "scan_id": str(scan.id),
                "mode": scan.mode,
                "entity_type": scan.entity_type,
            },
        )

        now = timezone.now()
        for member in members:
            recipient = QRAlertRecipient.objects.create(
                alert=alert,
                member=member,
                notify_role=member.notify_role,
                delivery_status="sent",
                notified_at=now,
            )
            if member.member_user_id:
                NotificationService.create(
                    user=member.member_user,
                    notif_type="qr_alert",
                    title=f"QR Alert: {scan.qr_code.label}",
                    body="You were notified as responder. If unavailable, mark unavailable so others can respond.",
                    organization=scan.qr_code.organization,
                    data={
                        "alert_id": str(alert.id),
                        "recipient_id": str(recipient.id),
                        "qr_code_id": str(scan.qr_code_id),
                        "scan_id": str(scan.id),
                        "notify_role": member.notify_role,
                        "member_type": member.member_type,
                    },
                    source_entity_type="qr_alert",
                    source_entity_id=str(alert.id),
                    priority="high",
                )

        return alert

    @staticmethod
    @transaction.atomic
    def respond(*, alert: QRAlert, member_id, response_status: str, response_note: str = "") -> QRAlertRecipient:
        recipient = QRAlertRecipient.objects.select_related("member").get(
            alert=alert,
            member_id=member_id,
        )
        recipient.response_status = response_status
        recipient.response_note = response_note or ""
        recipient.responded_at = timezone.now()
        recipient.save(update_fields=["response_status", "response_note", "responded_at"])

        if response_status == "accepted" and alert.status == "open":
            alert.status = "responded"
            alert.responded_by_member = recipient.member
            alert.responded_at = timezone.now()
            alert.save(update_fields=["status", "responded_by_member", "responded_at"])

        if response_status in {"unavailable", "declined"}:
            remaining = alert.recipients.filter(response_status="pending").exclude(pk=recipient.pk).exists()
            if not remaining and alert.status == "open":
                alert.status = "closed"
                alert.save(update_fields=["status"])

        return recipient
