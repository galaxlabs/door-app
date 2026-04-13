import secrets
from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from apps.qr_engine.models import QRCode, QRScan, ScanToken


class QRScanService:
    @staticmethod
    @transaction.atomic
    def create_scan_and_token(*, qr_code: QRCode, user=None, device_id: str = "", **extra) -> ScanToken:
        scan = QRScan.objects.create(
            qr_code=qr_code,
            scanned_by=user if user and user.is_authenticated else None,
            device_id=device_id,
            scan_source=extra.get("scan_source", "camera"),
            raw_content=extra.get("raw_content", ""),
            metadata=extra.get("metadata", {}),
            location_lat=extra.get("location_lat"),
            location_lng=extra.get("location_lng"),
            entity_type=qr_code.entity_type,
            mode=qr_code.mode,
            action_payload=qr_code.action_payload,
        )
        qr_code.scans_count += 1
        qr_code.save(update_fields=["scans_count"])
        return ScanToken.objects.create(
            scan=scan,
            token=secrets.token_hex(32),
            expires_at=timezone.now() + timedelta(minutes=30),
        )
