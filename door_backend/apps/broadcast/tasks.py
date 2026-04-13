"""Celery tasks for broadcast delivery via FCM and WebSocket."""
from celery import shared_task
from django.utils import timezone
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


@shared_task(bind=True, max_retries=3)
def send_broadcast_message(self, message_id: str):
    """Fan-out a broadcast message using target_mode and track per-recipient delivery."""
    from .models import (
        BroadcastMessage,
        BroadcastSubscription,
        BroadcastDelivery,
        BroadcastRecipient,
    )
    from apps.organizations.models import GroupMember, OrganizationMember
    from apps.auth_identity.models import UserDevice

    msg = BroadcastMessage.objects.get(pk=message_id)

    if msg.target_mode == "selected_members":
        user_ids = BroadcastRecipient.objects.filter(message=msg).values_list("user_id", flat=True)
    elif msg.target_mode == "group" and msg.channel.group_id:
        user_ids = GroupMember.objects.filter(
            group_id=msg.channel.group_id,
            membership_status="active",
            is_deleted=False,
        ).values_list("user_id", flat=True)
    else:
        # default: organization_members
        user_ids = OrganizationMember.objects.filter(
            organization=msg.channel.organization,
            membership_status="active",
            is_deleted=False,
        ).values_list("user_id", flat=True)

    muted_user_ids = BroadcastSubscription.objects.filter(
        channel=msg.channel,
        is_muted=True,
        is_deleted=False,
    ).values_list("user_id", flat=True)

    recipients = list(set(user_ids) - set(muted_user_ids))

    layer = get_channel_layer()

    delivered_count = 0
    for user_id in recipients:
        # Create delivery record
        delivery, _ = BroadcastDelivery.objects.get_or_create(
            message=msg,
            user_id=user_id,
            defaults={"status": "queued"},
        )

        # Push via WebSocket
        async_to_sync(layer.group_send)(
            f"broadcast_{msg.channel_id}",
            {
                "type": "ws_event",
                "event": "broadcast.message",
                "data": {
                    "id": str(msg.id),
                    "title": msg.title,
                    "body": msg.body,
                    "type": msg.type,
                    "target_mode": msg.target_mode,
                    "payload": msg.payload,
                },
            },
        )

        # Push via FCM to active devices
        tokens = list(
            UserDevice.objects.filter(user_id=user_id, is_active=True)
            .exclude(fcm_token="")
            .values_list("fcm_token", flat=True)
        )
        if tokens:
            try:
                from firebase_admin import messaging

                multicast = messaging.MulticastMessage(
                    notification=messaging.Notification(title=msg.title, body=msg.body),
                    tokens=tokens,
                    data={
                        "broadcast_message_id": str(msg.id),
                        "channel_id": str(msg.channel_id),
                    },
                )
                messaging.send_each_for_multicast(multicast)

                delivery.status = "delivered"
                delivery.delivered_at = timezone.now()
                delivery.save(update_fields=["status", "delivered_at"])
                delivered_count += 1
            except Exception as exc:
                delivery.status = "failed"
                delivery.failure_reason = str(exc)
                delivery.save(update_fields=["status", "failure_reason"])
        else:
            # WebSocket-only delivery path
            delivery.status = "sent"
            delivery.save(update_fields=["status"])

    msg.status = "sent"
    msg.sent_at = timezone.now()
    msg.save(update_fields=["status", "sent_at"])

    return {
        "message_id": str(msg.id),
        "recipients": len(recipients),
        "push_delivered": delivered_count,
    }


@shared_task(name="broadcast.send_scheduled_messages")
def send_scheduled_messages() -> int:
    """Dispatch scheduled broadcasts whose time has arrived."""
    from .models import BroadcastMessage

    due = BroadcastMessage.objects.filter(status="queued", scheduled_at__isnull=False, scheduled_at__lte=timezone.now())
    count = 0
    for msg in due.iterator():
        send_broadcast_message.delay(str(msg.id))
        count += 1
    return count
