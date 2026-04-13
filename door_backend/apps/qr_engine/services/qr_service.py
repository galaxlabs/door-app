from apps.qr_engine.models import QRCode


class QRService:
    @staticmethod
    def toggle_active(qr: QRCode, active: bool) -> QRCode:
        qr.is_active = active
        qr.status = "active" if active else "inactive"
        qr.save(update_fields=["is_active", "status"])
        return qr
