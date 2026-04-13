from apps.sync.models import SyncQueue, DeviceOutbox


class SyncSelector:
    @staticmethod
    def pending_uploads(user, device_id: str):
        return SyncQueue.objects.filter(user=user, device_id=device_id, status="pending").order_by("sequence")

    @staticmethod
    def pending_outbox(device_id: str):
        return DeviceOutbox.objects.filter(device_id=device_id, outbox_state="pending")
