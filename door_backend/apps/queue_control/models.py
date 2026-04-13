import uuid

from django.db import models
from django.db.models import Q, F
from django.conf import settings
from django.utils import timezone

from common.models import SoftDeleteModel


class Queue(SoftDeleteModel):
    STATUS_CHOICES = [
        ("open", "Open"),
        ("paused", "Paused"),
        ("closed", "Closed"),
    ]
    TYPE_CHOICES = [
        ("standard", "Standard"),
        ("priority", "Priority"),
        ("hybrid", "Hybrid"),
    ]

    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="queues",
    )
    event = models.ForeignKey(
        "organizations.Event",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="queues",
    )
    group = models.ForeignKey(
        "organizations.Group",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="queues",
    )

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    queue_type = models.CharField(max_length=16, choices=TYPE_CHOICES, default="standard")
    max_capacity = models.PositiveIntegerField(default=0, help_text="0 = unlimited")
    current_serving = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="open", db_index=True)
    allow_rejoin = models.BooleanField(default=False)
    is_token_based = models.BooleanField(default=True)
    estimated_wait_minutes = models.PositiveIntegerField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "queues"
        indexes = [
            models.Index(fields=["organization", "status"]),
            models.Index(fields=["event"]),
            models.Index(fields=["group"]),
            models.Index(fields=["updated_at_server"]),
        ]
        constraints = [
            models.CheckConstraint(check=Q(max_capacity__gte=0), name="queue_max_capacity_gte_0"),
            models.CheckConstraint(check=Q(current_serving__gte=0), name="queue_current_serving_gte_0"),
        ]

    def __str__(self):
        return f"Queue:{self.name}"

    @property
    def waiting_count(self):
        # Compatibility: treat `issued` as canonical waiting token state.
        return self.tickets.filter(status__in=["issued", "waiting"]).count()


class QueueSession(SoftDeleteModel):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("paused", "Paused"),
        ("ended", "Ended"),
    ]

    queue = models.ForeignKey(Queue, on_delete=models.CASCADE, related_name="sessions")
    started_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="started_queue_sessions",
    )
    ended_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ended_queue_sessions",
    )

    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default="active", db_index=True)
    started_at = models.DateTimeField(default=timezone.now)
    ended_at = models.DateTimeField(null=True, blank=True)

    current_token_number = models.PositiveIntegerField(default=0)
    last_called_token_number = models.PositiveIntegerField(null=True, blank=True)

    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "queue_sessions"
        indexes = [
            models.Index(fields=["queue", "status"]),
            models.Index(fields=["started_at"]),
            models.Index(fields=["updated_at_server"]),
        ]
        constraints = [
            models.CheckConstraint(
                check=Q(ended_at__isnull=True) | Q(ended_at__gte=F("started_at")),
                name="queue_session_end_after_start",
            ),
            # One active session per queue at DB level.
            models.UniqueConstraint(
                fields=["queue"],
                condition=Q(status="active"),
                name="unique_active_session_per_queue",
            ),
        ]

    def __str__(self):
        return f"Session({self.queue.name}, {self.status})"


class QueueTicket(SoftDeleteModel):
    STATUS_CHOICES = [
        # Canonical Phase-1 token states:
        ("issued", "Issued"),
        ("waiting", "Waiting"),
        ("called", "Called"),
        ("recalled", "Recalled"),
        ("completed", "Completed"),
        ("serving", "Serving"),
        ("done", "Done"),
        ("skipped", "Skipped"),
        ("cancelled", "Cancelled"),
    ]

    queue = models.ForeignKey(Queue, on_delete=models.CASCADE, related_name="tickets")
    session = models.ForeignKey(
        QueueSession,
        on_delete=models.CASCADE,
        related_name="tickets",
        null=True,
        blank=True,
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="queue_tickets",
    )
    issued_from_scan_token = models.ForeignKey(
        "qr_engine.ScanToken",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="issued_tickets",
    )

    device_id = models.CharField(max_length=128, blank=True)
    number = models.PositiveIntegerField()
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default="issued", db_index=True)
    priority = models.PositiveSmallIntegerField(default=0)
    desk_number = models.PositiveIntegerField(null=True, blank=True)
    issued_at = models.DateTimeField(default=timezone.now)
    called_at = models.DateTimeField(null=True, blank=True)
    recalled_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    served_at = models.DateTimeField(null=True, blank=True)  # backward-compat alias usage
    estimated_wait_snapshot = models.PositiveIntegerField(null=True, blank=True)
    notes = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "queue_tickets"
        unique_together = [("session", "number")]
        ordering = ["number"]
        indexes = [
            models.Index(fields=["queue", "status", "number"]),
            models.Index(fields=["session", "status", "number"]),
            models.Index(fields=["user", "status"]),
            models.Index(fields=["issued_at"]),
            models.Index(fields=["updated_at_server"]),
        ]
        constraints = [
            models.CheckConstraint(check=Q(number__gte=1), name="queue_ticket_number_gte_1"),
            models.CheckConstraint(check=Q(priority__gte=0), name="queue_ticket_priority_gte_0"),
        ]

    def __str__(self):
        return f"T#{self.number} [{self.queue}] {self.status}"


class QueueActionLog(models.Model):
    ACTION_CHOICES = [
        ("next", "Next"),
        ("call", "Call"),
        ("skip", "Skip"),
        ("recall", "Recall"),
        ("complete", "Complete"),
        ("cancel", "Cancel"),
        ("session_open", "Session Open"),
        ("session_close", "Session Close"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    queue = models.ForeignKey(Queue, on_delete=models.CASCADE, related_name="action_logs")
    session = models.ForeignKey(
        QueueSession,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="action_logs",
    )
    ticket = models.ForeignKey(
        QueueTicket,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="action_logs",
    )
    actor_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="queue_actions",
    )
    actor_device_id = models.CharField(max_length=128, blank=True)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, db_index=True)
    before_state = models.JSONField(default=dict, blank=True)
    after_state = models.JSONField(default=dict, blank=True)
    meta = models.JSONField(default=dict, blank=True)
    created_at_server = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "queue_action_logs"
        indexes = [
            models.Index(fields=["queue", "created_at_server"]),
            models.Index(fields=["session", "created_at_server"]),
            models.Index(fields=["ticket", "created_at_server"]),
            models.Index(fields=["actor_user", "created_at_server"]),
            models.Index(fields=["action", "created_at_server"]),
        ]

    def __str__(self):
        return f"QueueAction({self.action})"
