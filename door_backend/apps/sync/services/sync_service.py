from django.db import transaction
from django.utils import timezone

from apps.sync.models import SyncQueue, SyncCursor


class SyncService:
    @staticmethod
    @transaction.atomic
    def ingest_operations(*, user, device_id: str, operations: list, stream_name: str = "core"):
        created = []
        for op in operations:
            item = SyncQueue.objects.create(
                user=user,
                device_id=device_id,
                operation=op["operation"],
                entity_type=op["entity_type"],
                entity_id=op.get("entity_id", ""),
                client_id=op.get("client_id", ""),
                idempotency_key=op.get("idempotency_key"),
                payload=op.get("payload", {}),
                sequence=op.get("sequence", 0),
                created_at_client=op.get("created_at_client"),
                updated_at_client=op.get("updated_at_client"),
                status="pending",
            )
            created.append(item)

        SyncCursor.objects.update_or_create(
            user=user,
            device_id=device_id,
            stream_name=stream_name,
            defaults={"last_sync_at": timezone.now()},
        )
        return created
