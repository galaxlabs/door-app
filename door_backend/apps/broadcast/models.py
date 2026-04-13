from django.db import models
from django.conf import settings
from common.models import SoftDeleteModel


class BroadcastChannel(SoftDeleteModel):
    TYPE_CHOICES = [
        ("public", "Public"),
        ("private", "Private"),
        ("staff_only", "Staff Only"),
    ]

    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="broadcast_channels",
    )
    group = models.ForeignKey(
        "organizations.Group",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="broadcast_channels",
    )
    interaction = models.ForeignKey(
        "qr_engine.InteractionRecord",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="broadcast_channels",
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default="public")
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        db_table = "broadcast_channels"
        indexes = [
            models.Index(fields=["organization", "is_active"]),
            models.Index(fields=["group"]),
            models.Index(fields=["interaction"]),
            models.Index(fields=["updated_at_server"]),
        ]
        unique_together = [("organization", "name")]

    def __str__(self):
        return f"BC:{self.name}"


class BroadcastSubscription(SoftDeleteModel):
    channel = models.ForeignKey(BroadcastChannel, on_delete=models.CASCADE, related_name="subscriptions")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="subscriptions")
    subscribed_at = models.DateTimeField(auto_now_add=True)
    is_muted = models.BooleanField(default=False)

    class Meta:
        db_table = "broadcast_subscriptions"
        unique_together = [("channel", "user")]
        indexes = [
            models.Index(fields=["channel", "is_muted"]),
            models.Index(fields=["user", "updated_at_server"]),
        ]


class BroadcastMessage(SoftDeleteModel):
    TYPE_CHOICES = [
        ("info", "Info"),
        ("alert", "Alert"),
        ("call_number", "Call Number"),
        ("custom", "Custom"),
    ]
    TARGET_MODE_CHOICES = [
        ("group", "Group"),
        ("organization_members", "Organization Members"),
        ("selected_members", "Selected Members"),
    ]
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("queued", "Queued"),
        ("sent", "Sent"),
        ("failed", "Failed"),
    ]

    channel = models.ForeignKey(BroadcastChannel, on_delete=models.CASCADE, related_name="messages")
    interaction = models.ForeignKey(
        "qr_engine.InteractionRecord",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="broadcast_messages",
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="broadcast_messages"
    )
    title = models.CharField(max_length=255)
    body = models.TextField()
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default="info")
    target_mode = models.CharField(max_length=24, choices=TARGET_MODE_CHOICES, default="organization_members")
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default="queued", db_index=True)
    payload = models.JSONField(default=dict, blank=True)
    sent_at = models.DateTimeField(auto_now_add=True)
    scheduled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "broadcast_messages"
        ordering = ["-sent_at"]
        indexes = [
            models.Index(fields=["channel", "sent_at"]),
            models.Index(fields=["interaction", "sent_at"]),
            models.Index(fields=["target_mode", "status"]),
            models.Index(fields=["scheduled_at"]),
            models.Index(fields=["updated_at_server"]),
        ]

    def __str__(self):
        return f"BCMsg:{self.title}"


class BroadcastDelivery(SoftDeleteModel):
    STATUS_CHOICES = [
        ("queued", "Queued"),
        ("sent", "Sent"),
        ("delivered", "Delivered"),
        ("seen", "Seen"),
        ("failed", "Failed"),
    ]

    message = models.ForeignKey(BroadcastMessage, on_delete=models.CASCADE, related_name="deliveries")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="deliveries")
    device_id = models.CharField(max_length=128, blank=True)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default="queued", db_index=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)
    failure_reason = models.TextField(blank=True)

    class Meta:
        db_table = "broadcast_deliveries"
        unique_together = [("message", "user")]
        indexes = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["message", "status"]),
            models.Index(fields=["device_id"]),
            models.Index(fields=["updated_at_server"]),
        ]


class BroadcastRecipient(SoftDeleteModel):
    """Explicit recipient table for selected-member targeting."""

    message = models.ForeignKey(
        BroadcastMessage,
        on_delete=models.CASCADE,
        related_name="recipients",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="broadcast_recipients",
    )

    class Meta:
        db_table = "broadcast_recipients"
        unique_together = [("message", "user")]
        indexes = [
            models.Index(fields=["message"]),
            models.Index(fields=["user"]),
            models.Index(fields=["updated_at_server"]),
        ]
