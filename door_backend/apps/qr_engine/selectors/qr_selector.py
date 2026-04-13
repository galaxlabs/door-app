from django.utils import timezone
from django.db.models import Q

from apps.qr_engine.models import QRCode


class QRSelector:
    @staticmethod
    def active_qr_queryset():
        now = timezone.now()
        return QRCode.objects.filter(is_active=True, status="active").filter(
            Q(expires_at__isnull=True) | Q(expires_at__gt=now)
        )
