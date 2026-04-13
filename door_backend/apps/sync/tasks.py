"""Background jobs for generic offline sync domain."""

from celery import shared_task
from django.utils import timezone


@shared_task(name="sync.process_pending_queue")
def process_pending_queue(batch_size: int = 200) -> int:
    """
    Process pending sync queue items in FIFO order.

    NOTE: core apply logic remains in sync engine/service; this task is orchestration.
    """
    from .models import SyncQueue

    items = list(SyncQueue.objects.filter(status="pending").order_by("sequence", "created_at_server")[:batch_size])
    processed = 0
    for item in items:
        item.status = "processing"
        item.save(update_fields=["status", "updated_at_server"])
        # Placeholder orchestration mark (actual domain apply occurs in sync engine step)
        item.status = "applied"
        item.synced_at = timezone.now()
        item.save(update_fields=["status", "synced_at", "updated_at_server"])
        processed += 1
    return processed


@shared_task(name="sync.dispatch_device_outbox")
def dispatch_device_outbox(batch_size: int = 300) -> int:
    """Mark pending outbox records as dispatched for downstream delivery workers."""
    from .models import DeviceOutbox

    rows = list(DeviceOutbox.objects.filter(outbox_state="pending").order_by("created_at_server")[:batch_size])
    for row in rows:
        row.outbox_state = "dispatched"
        row.save(update_fields=["outbox_state"])
    return len(rows)
