from django.utils import timezone

from apps.notifications.models import Notification


class NotificationService:
    @staticmethod
    def create(*, user, notif_type: str, title: str, body: str, **kwargs) -> Notification:
        return Notification.objects.create(
            user=user,
            organization=kwargs.get("organization"),
            type=notif_type,
            title=title,
            body=body,
            data=kwargs.get("data", {}),
            priority=kwargs.get("priority", "normal"),
            source_entity_type=kwargs.get("source_entity_type", ""),
            source_entity_id=kwargs.get("source_entity_id", ""),
        )

    @staticmethod
    def mark_read(notification: Notification) -> Notification:
        notification.state = "read"
        notification.read_at = timezone.now()
        notification.save(update_fields=["state", "read_at", "is_read"])
        return notification
