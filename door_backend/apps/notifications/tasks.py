"""Background jobs for notifications domain."""

from celery import shared_task
from django.utils import timezone


@shared_task(name="notifications.archive_expired")
def archive_expired_notifications() -> int:
    """Archive notifications once their expiry is reached."""
    from .models import Notification

    return Notification.objects.filter(
        state__in=["unread", "read"],
        expires_at__isnull=False,
        expires_at__lt=timezone.now(),
    ).update(state="archived", archived_at=timezone.now())


@shared_task(name="notifications.send_push_for_notification")
def send_push_for_notification(notification_id: str) -> bool:
    """Send push notification to all active user devices (FCM)."""
    from .models import Notification
    from apps.auth_identity.models import UserDevice

    try:
        notif = Notification.objects.get(pk=notification_id)
    except Notification.DoesNotExist:
        return False

    tokens = list(
        UserDevice.objects.filter(user=notif.user, is_active=True)
        .exclude(fcm_token="")
        .values_list("fcm_token", flat=True)
    )
    if not tokens:
        return True

    try:
        from firebase_admin import messaging

        multicast = messaging.MulticastMessage(
            notification=messaging.Notification(title=notif.title, body=notif.body),
            data={
                "notification_id": str(notif.id),
                "type": notif.type,
                "source_entity_type": notif.source_entity_type,
                "source_entity_id": notif.source_entity_id,
            },
            tokens=tokens,
        )
        messaging.send_each_for_multicast(multicast)
    except Exception:
        return False

    return True
