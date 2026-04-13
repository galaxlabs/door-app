from django.db import models
from django.conf import settings
import uuid


class AuditLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
    )
    action = models.CharField(max_length=255, db_index=True)
    entity_type = models.CharField(max_length=100, blank=True, db_index=True)
    entity_id = models.CharField(max_length=64, blank=True, db_index=True)

    # Compatibility/general payload
    payload = models.JSONField(default=dict, blank=True)

    # Rich audit snapshots
    before_json = models.JSONField(default=dict, blank=True)
    after_json = models.JSONField(default=dict, blank=True)
    context_json = models.JSONField(default=dict, blank=True)

    ip_address = models.GenericIPAddressField(null=True, blank=True)
    device_id = models.CharField(max_length=128, blank=True)
    user_agent = models.TextField(blank=True)
    request_id = models.CharField(max_length=128, blank=True, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    created_at_server = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "audit_logs"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["organization", "created_at_server"]),
            models.Index(fields=["user", "created_at_server"]),
            models.Index(fields=["entity_type", "entity_id", "created_at_server"]),
            models.Index(fields=["action", "created_at_server"]),
            models.Index(fields=["request_id"]),
        ]

    def __str__(self):
        return f"Audit:{self.action} by {self.user_id}"
