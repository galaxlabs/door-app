from apps.audit.models import AuditLog


class AuditService:
    @staticmethod
    def log(*, actor=None, organization=None, action: str, entity_type: str = "", entity_id: str = "", **context):
        return AuditLog.objects.create(
            user=actor,
            organization=organization,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            payload=context.get("payload", {}),
            before_json=context.get("before_json", {}),
            after_json=context.get("after_json", {}),
            context_json=context.get("context_json", {}),
            ip_address=context.get("ip_address"),
            device_id=context.get("device_id", ""),
            user_agent=context.get("user_agent", ""),
            request_id=context.get("request_id", ""),
        )
