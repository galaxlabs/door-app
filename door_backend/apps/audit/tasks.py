"""Background jobs for audit domain."""

from datetime import timedelta

from celery import shared_task
from django.utils import timezone


@shared_task(name="audit.prune_old_logs")
def prune_old_logs(retention_days: int = 365) -> int:
    """Delete very old audit records based on retention policy."""
    from .models import AuditLog

    cutoff = timezone.now() - timedelta(days=retention_days)
    deleted, _ = AuditLog.objects.filter(created_at_server__lt=cutoff).delete()
    return deleted
