from django.utils import timezone

from apps.sync.models import ConflictLog


class ConflictService:
    @staticmethod
    def resolve(*, conflict: ConflictLog, resolution: str):
        conflict.resolution = resolution
        conflict.resolved_at = timezone.now()
        conflict.save(update_fields=["resolution", "resolved_at"])
        return conflict
