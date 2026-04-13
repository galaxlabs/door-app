from django.db import models
from django.conf import settings
from common.models import SoftDeleteModel


class ChatRoom(SoftDeleteModel):
    TYPE_CHOICES = [
        ("direct", "Direct"),
        ("group", "Group"),
        ("event", "Event Channel"),
        ("organization", "Organization Channel"),
    ]
    STATUS_CHOICES = [
        ("active", "Active"),
        ("archived", "Archived"),
    ]

    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.SET_NULL,
        related_name="chat_rooms",
        null=True,
        blank=True,
    )
    event = models.ForeignKey(
        "organizations.Event",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="chat_rooms",
    )
    group = models.ForeignKey(
        "organizations.Group",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="chat_rooms",
    )

    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default="group")
    name = models.CharField(max_length=255, blank=True)
    avatar = models.ImageField(upload_to="chat_avatars/", blank=True, null=True)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default="active", db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_chat_rooms",
    )
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "chat_rooms"
        indexes = [
            models.Index(fields=["organization", "status"]),
            models.Index(fields=["event"]),
            models.Index(fields=["group"]),
            models.Index(fields=["type", "is_active"]),
            models.Index(fields=["updated_at_server"]),
        ]

    def __str__(self):
        return f"Room:{self.name or self.id}"


class ChatRoomMember(SoftDeleteModel):
    ROLE_CHOICES = [
        ("member", "Member"),
        ("moderator", "Moderator"),
        ("admin", "Admin"),
    ]

    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name="members")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="chat_memberships"
    )
    is_admin = models.BooleanField(default=False)
    role = models.CharField(max_length=16, choices=ROLE_CHOICES, default="member", db_index=True)
    last_read_at = models.DateTimeField(null=True, blank=True)
    joined_at = models.DateTimeField(auto_now_add=True)
    left_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "chat_room_members"
        unique_together = [("room", "user")]
        indexes = [
            models.Index(fields=["room", "role"]),
            models.Index(fields=["user", "updated_at_server"]),
        ]


class ChatMessage(SoftDeleteModel):
    TYPE_CHOICES = [
        ("text", "Text"),
        ("image_placeholder", "Image Placeholder"),
        ("voice_placeholder", "Voice Placeholder"),
        # Backward-compatible legacy values
        ("image", "Image"),
        ("file", "File"),
        ("audio", "Audio"),
        ("system", "System"),
    ]
    DELIVERY_STATE_CHOICES = [
        ("queued", "Queued"),
        ("sent", "Sent"),
        ("delivered", "Delivered"),
        ("seen", "Seen"),
    ]

    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="sent_messages",
    )
    sender_device_id = models.CharField(max_length=128, blank=True)
    type = models.CharField(max_length=24, choices=TYPE_CHOICES, default="text")
    content = models.TextField(blank=True)
    attachment = models.FileField(upload_to="chat_attachments/", blank=True, null=True)
    reply_to = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, blank=True, related_name="replies"
    )
    delivery_state = models.CharField(
        max_length=12,
        choices=DELIVERY_STATE_CHOICES,
        default="queued",
        db_index=True,
    )
    sent_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(null=True, blank=True)
    client_id = models.CharField(
        max_length=64,
        blank=True,
        db_index=True,
        help_text="Client-generated idempotency ID for offline sync",
    )

    class Meta:
        db_table = "chat_messages"
        ordering = ["sent_at"]
        indexes = [
            models.Index(fields=["room", "sent_at"]),
            models.Index(fields=["sender", "sent_at"]),
            models.Index(fields=["delivery_state", "sent_at"]),
            models.Index(fields=["client_id"]),
            models.Index(fields=["updated_at_server"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["sender", "client_id"],
                condition=~models.Q(client_id=""),
                name="chat_message_sender_client_id_unique",
            )
        ]

    def __str__(self):
        return f"Msg[{self.room}] by {self.sender}"


class MessageStatus(SoftDeleteModel):
    STATUS_CHOICES = [
        ("queued", "Queued"),
        ("sent", "Sent"),
        ("delivered", "Delivered"),
        ("seen", "Seen"),
    ]

    message = models.ForeignKey(ChatMessage, on_delete=models.CASCADE, related_name="statuses")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="+")
    status = models.CharField(max_length=12, choices=STATUS_CHOICES)
    status_device_id = models.CharField(max_length=128, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "chat_message_statuses"
        unique_together = [("message", "user")]
        indexes = [
            models.Index(fields=["user", "status", "updated_at"]),
            models.Index(fields=["message", "updated_at"]),
        ]
