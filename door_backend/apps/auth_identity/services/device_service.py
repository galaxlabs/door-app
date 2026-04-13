from apps.auth_identity.models import UserDevice


class DeviceService:
    @staticmethod
    def register_or_update_device(*, user, device_id: str, platform: str, **extra) -> UserDevice:
        obj, _ = UserDevice.objects.update_or_create(
            user=user,
            device_id=device_id,
            defaults={
                "platform": platform,
                "app_version": extra.get("app_version", ""),
                "fcm_token": extra.get("fcm_token", ""),
                "device_name": extra.get("device_name", ""),
                "os_version": extra.get("os_version", ""),
                "notification_enabled": extra.get("notification_enabled", True),
                "is_active": True,
            },
        )
        return obj
