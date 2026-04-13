import uuid
from django.db import models


class UUIDModel(models.Model):
    """Simple base model with UUID primary key and server timestamps."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        abstract = True


class SyncableModel(models.Model):
    """
    Base model for offline-first syncable entities.

    IMPORTANT:
    - Use this in domain tables that participate in mobile/web offline sync.
    - Keep UUID primary key and explicit client/server timestamps.
    """

    class SyncStatus(models.TextChoices):
        PENDING_LOCAL = "pending_local", "Pending Local"
        QUEUED_SYNC = "queued_sync", "Queued Sync"
        SYNCED = "synced", "Synced"
        CONFLICT = "conflict", "Conflict"
        FAILED = "failed", "Failed"
        DELETED = "deleted", "Deleted"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Client-origin timestamps (nullable because server-origin records may not have them)
    created_at_client = models.DateTimeField(null=True, blank=True)
    updated_at_client = models.DateTimeField(null=True, blank=True)

    # Server-truth timestamps
    created_at_server = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at_server = models.DateTimeField(auto_now=True, db_index=True)

    # Sync metadata
    sync_status = models.CharField(
        max_length=24,
        choices=SyncStatus.choices,
        default=SyncStatus.SYNCED,
        db_index=True,
    )
    version = models.BigIntegerField(default=1)
    created_by_device_id = models.CharField(max_length=128, blank=True)
    last_modified_by_device_id = models.CharField(max_length=128, blank=True)
    idempotency_key = models.UUIDField(null=True, blank=True, db_index=True)

    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=["updated_at_server"]),
            models.Index(fields=["sync_status", "updated_at_server"]),
        ]


class SoftDeleteModel(SyncableModel):
    """Syncable base model supporting soft-delete semantics."""

    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True
