from django.db import models
from django.conf import settings
from common.models import UUIDModel


class SyncCursor(UUIDModel):
    """Per device/stream sync cursor for delta pull."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sync_cursors")
    device_id = models.CharField(max_length=128)
    stream_name = models.CharField(max_length=50, default="core")
    last_sync_at = models.DateTimeField(null=True, blank=True)
    last_seen_version = models.BigIntegerField(default=0)
    cursor_token = models.CharField(max_length=255, blank=True)
    entity_types = models.JSONField(default=list, blank=True, help_text="List of entity types tracked")

    class Meta:
        db_table = "sync_cursors"
        unique_together = [("device_id", "stream_name")]
        indexes = [
            models.Index(fields=["user", "device_id"]),
            models.Index(fields=["stream_name", "last_sync_at"]),
        ]

    def __str__(self):
        return f"SyncCursor:{self.user}/{self.device_id}/{self.stream_name}"


class SyncSession(SyncCursor):
    """Backward-compat alias model (same shape) for older imports."""

    class Meta:
        proxy = True


class SyncQueue(UUIDModel):
    """Client-side operations queued for upload."""

    OPERATION_CHOICES = [
        ("create", "Create"),
        ("update", "Update"),
        ("delete", "Delete"),
        ("action", "Action"),
    ]
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("applied", "Applied"),
        ("conflict", "Conflict"),
        ("failed", "Failed"),
        ("ignored_duplicate", "Ignored Duplicate"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sync_queue")
    device_id = models.CharField(max_length=128, db_index=True)
    operation = models.CharField(max_length=10, choices=OPERATION_CHOICES)
    entity_type = models.CharField(max_length=100, db_index=True)
    entity_id = models.CharField(max_length=64, blank=True, db_index=True)
    client_id = models.CharField(max_length=64, blank=True, help_text="Client-generated UUID for new records")
    idempotency_key = models.UUIDField(null=True, blank=True, db_index=True)
    created_at_client = models.DateTimeField(null=True, blank=True)
    updated_at_client = models.DateTimeField(null=True, blank=True)
    created_at_server = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at_server = models.DateTimeField(auto_now=True, db_index=True)
    payload = models.JSONField(default=dict)
    status = models.CharField(max_length=24, choices=STATUS_CHOICES, default="pending")
    error_detail = models.TextField(blank=True)
    cursor_before = models.CharField(max_length=255, blank=True)
    cursor_after = models.CharField(max_length=255, blank=True)
    synced_at = models.DateTimeField(null=True, blank=True)
    sequence = models.PositiveBigIntegerField(help_text="Client-side sequence number for ordering")

    class Meta:
        db_table = "sync_queue"
        ordering = ["sequence"]
        indexes = [
            models.Index(fields=["user", "status", "created_at_server"]),
            models.Index(fields=["entity_type", "entity_id"]),
            models.Index(fields=["device_id", "created_at_server"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["device_id", "idempotency_key"],
                condition=~models.Q(idempotency_key=None),
                name="sync_queue_device_idempotency_unique",
            )
        ]

    def __str__(self):
        return f"SyncQ:{self.operation}/{self.entity_type}/{self.entity_id}"


class DeviceOutbox(UUIDModel):
    """Server-to-device outbound queue for delta/event fanout."""

    STATE_CHOICES = [
        ("pending", "Pending"),
        ("dispatched", "Dispatched"),
        ("acked", "Acked"),
        ("dead_letter", "Dead Letter"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="device_outbox")
    device_id = models.CharField(max_length=128, db_index=True)
    entity_type = models.CharField(max_length=100, db_index=True)
    entity_id = models.CharField(max_length=64, db_index=True)
    operation = models.CharField(max_length=20)
    payload = models.JSONField(default=dict)
    event_version = models.BigIntegerField(default=1)
    outbox_state = models.CharField(max_length=12, choices=STATE_CHOICES, default="pending", db_index=True)
    retry_count = models.PositiveIntegerField(default=0)
    next_retry_at = models.DateTimeField(null=True, blank=True)
    acked_at = models.DateTimeField(null=True, blank=True)
    created_at_server = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "device_outbox"
        indexes = [
            models.Index(fields=["device_id", "outbox_state", "next_retry_at"]),
            models.Index(fields=["user", "outbox_state"]),
            models.Index(fields=["created_at_server"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["device_id", "entity_type", "entity_id", "event_version", "operation"],
                name="device_outbox_event_unique",
            )
        ]

    def __str__(self):
        return f"Outbox:{self.device_id}/{self.entity_type}/{self.entity_id}"


class ConflictLog(UUIDModel):
    RESOLUTION_CHOICES = [
        ("server_wins", "Server Wins"),
        ("client_wins", "Client Wins"),
        ("merged", "Merged"),
        ("manual", "Manual"),
    ]

    sync_queue_item = models.ForeignKey(SyncQueue, on_delete=models.SET_NULL, null=True, related_name="conflicts")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sync_conflicts")
    entity_type = models.CharField(max_length=100)
    entity_id = models.CharField(max_length=64)
    server_version = models.JSONField(default=dict)
    client_version = models.JSONField(default=dict)
    resolution = models.CharField(max_length=15, choices=RESOLUTION_CHOICES, default="server_wins")
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "sync_conflicts"
        indexes = [
            models.Index(fields=["user", "resolved_at"]),
            models.Index(fields=["entity_type", "entity_id"]),
        ]
