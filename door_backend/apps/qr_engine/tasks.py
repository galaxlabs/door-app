"""Background jobs for qr_engine domain."""

from celery import shared_task
from django.utils import timezone


@shared_task(name="qr_engine.expire_scan_tokens")
def expire_scan_tokens() -> int:
    """Expire issued scan tokens that passed expiry timestamp."""
    from .models import ScanToken

    return ScanToken.objects.filter(
        status="issued",
        expires_at__lt=timezone.now(),
    ).update(status="expired")


@shared_task(name="qr_engine.deactivate_expired_qr_codes")
def deactivate_expired_qr_codes() -> int:
    """Deactivate QR codes once expiry time has passed."""
    from .models import QRCode

    return QRCode.objects.filter(
        is_active=True,
        status="active",
        expires_at__isnull=False,
        expires_at__lt=timezone.now(),
    ).update(is_active=False, status="inactive")
