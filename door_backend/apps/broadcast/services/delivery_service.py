from django.utils import timezone

from apps.broadcast.models import BroadcastDelivery


class BroadcastDeliveryService:
    @staticmethod
    def mark_delivered(delivery: BroadcastDelivery):
        delivery.status = "delivered"
        delivery.delivered_at = timezone.now()
        delivery.save(update_fields=["status", "delivered_at"])
        return delivery

    @staticmethod
    def mark_seen(delivery: BroadcastDelivery):
        delivery.status = "seen"
        delivery.read_at = timezone.now()
        delivery.save(update_fields=["status", "read_at"])
        return delivery
