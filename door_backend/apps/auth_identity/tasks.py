"""Background jobs for auth_identity domain."""
from datetime import timedelta

from celery import shared_task
from django.utils import timezone


@shared_task(name="auth_identity.expire_pending_otps")
def expire_pending_otps() -> int:
    """Mark stale OTP requests as expired."""
    from .models import OTP

    updated = OTP.objects.filter(
        used=False,
        status=OTP.Status.PENDING,
        expires_at__lt=timezone.now(),
    ).update(status=OTP.Status.EXPIRED)
    return updated


@shared_task(name="auth_identity.revoke_expired_sessions")
def revoke_expired_sessions() -> int:
    """Revoke user sessions whose refresh token expiry has passed."""
    from .models import UserSession

    updated = UserSession.objects.filter(
        status=UserSession.Status.ACTIVE,
        expires_at__lt=timezone.now(),
    ).update(status=UserSession.Status.EXPIRED)
    return updated


@shared_task(name="auth_identity.deactivate_stale_devices")
def deactivate_stale_devices(days: int = 90) -> int:
    """Deactivate devices that have not been seen in a long time."""
    from .models import UserDevice

    cutoff = timezone.now() - timedelta(days=days)
    return UserDevice.objects.filter(last_seen__lt=cutoff, is_active=True).update(is_active=False)
