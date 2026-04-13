from django.db import transaction

from apps.broadcast.models import BroadcastMessage, BroadcastRecipient


class BroadcastService:
    @staticmethod
    @transaction.atomic
    def create_message(*, channel, sender, title, body, target_mode, payload=None, selected_users=None):
        msg = BroadcastMessage.objects.create(
            channel=channel,
            interaction=getattr(channel, "interaction", None),
            sender=sender,
            title=title,
            body=body,
            type=(payload or {}).get("type", "info"),
            target_mode=target_mode,
            payload=payload or {},
            status="queued",
        )
        if target_mode == "selected_members" and selected_users:
            BroadcastRecipient.objects.bulk_create(
                [BroadcastRecipient(message=msg, user=u) for u in selected_users],
                ignore_conflicts=True,
            )
        return msg
