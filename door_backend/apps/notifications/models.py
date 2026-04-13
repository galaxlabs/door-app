from django.db import models
from django.conf import settings
from common.models import SoftDeleteModel


class Notification(SoftDeleteModel):
    TYPE_CHOICES = [
        ("queue_called", "Queue Called"),
        ("broadcast_delivery", "Broadcast Delivery"),
        ("chat_message", "Chat Message"),
        ("qr_alert", "QR Alert"),
        ("event_update", "Event Update"),
        ("system", "System"),
    ]
    PRIORITY_CHOICES = [
        ("low", "Low"),
        ("normal", "Normal"),
        ("high", "High"),
        ("critical", "Critical"),
    ]
    STATE_CHOICES = [
        ("unread", "Unread"),
        ("read", "Read"),
        ("archived", "Archived"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications"
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="notifications",
    )

    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    title = models.CharField(max_length=255)
    body = models.TextField()
    data = models.JSONField(default=dict, blank=True)

    priority = models.CharField(max_length=12, choices=PRIORITY_CHOICES, default="normal")
    state = models.CharField(max_length=12, choices=STATE_CHOICES, default="unread", db_index=True)

    source_entity_type = models.CharField(max_length=100, blank=True)
    source_entity_id = models.CharField(max_length=64, blank=True)

    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    archived_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "notifications"
        ordering = ["-created_at_server"]
        indexes = [
            models.Index(fields=["user", "state", "created_at_server"]),
            models.Index(fields=["type"]),
            models.Index(fields=["source_entity_type", "source_entity_id"]),
            models.Index(fields=["updated_at_server"]),
        ]

    def __str__(self):
        return f"Notif:{self.type} for {self.user_id}"

    def save(self, *args, **kwargs):
        # Backward-compat bridge for existing code using `is_read`.
        if self.state == "read":
            self.is_read = True
        elif self.state == "unread":
            self.is_read = False

        if self.is_read and self.state == "unread":
            self.state = "read"

        super().save(*args, **kwargs)
