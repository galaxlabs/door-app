"""
Sync Engine — processes client upload batches with idempotency and conflict detection.

Design:
  - Client sends a batch of operations (create/update/delete) with sequence numbers.
  - Server applies them in order; skips already-applied client_ids.
  - Returns full diff since last_sync_at for client to apply locally.
  - Conflicts: if server record changed since client last sync, log ConflictLog (server wins by default).
"""
from django.utils import timezone
from .models import SyncQueue, SyncSession, ConflictLog

# Map entity_type → (Model, Serializer)
ENTITY_REGISTRY: dict = {}


def register_entity(entity_type: str, model, serializer_class):
    ENTITY_REGISTRY[entity_type] = (model, serializer_class)


def process_upload_batch(user, device_id: str, operations: list) -> dict:
    """
    Process a list of operations from the client.
    Returns { applied: [...], conflicts: [...], errors: [...] }
    """
    session, _ = SyncSession.objects.get_or_create(
        user=user, device_id=device_id, defaults={"entity_types": []}
    )

    applied = []
    conflicts = []
    errors = []

    for op in sorted(operations, key=lambda o: o.get("sequence", 0)):
        entity_type = op.get("entity_type")
        operation = op.get("operation")
        client_id = op.get("client_id", "")
        entity_id = op.get("entity_id", "")
        payload = op.get("payload", {})
        sequence = op.get("sequence", 0)

        # Idempotency: skip already synced
        if client_id and SyncQueue.objects.filter(
            user=user, client_id=client_id, status="synced"
        ).exists():
            applied.append({"client_id": client_id, "skipped": True})
            continue

        queue_item = SyncQueue.objects.create(
            user=user,
            device_id=device_id,
            operation=operation,
            entity_type=entity_type,
            entity_id=entity_id,
            client_id=client_id,
            payload=payload,
            sequence=sequence,
            status="processing",
        )

        try:
            result = _apply_operation(user, queue_item, session)
            queue_item.status = "synced"
            queue_item.synced_at = timezone.now()
            queue_item.save(update_fields=["status", "synced_at"])
            applied.append({"client_id": client_id, "server_id": result})
        except ConflictError as e:
            queue_item.status = "conflict"
            queue_item.save(update_fields=["status"])
            conflict = ConflictLog.objects.create(
                sync_queue_item=queue_item,
                user=user,
                entity_type=entity_type,
                entity_id=entity_id,
                server_version=e.server_version,
                client_version=payload,
            )
            conflicts.append({"client_id": client_id, "conflict_id": str(conflict.id)})
        except Exception as e:
            queue_item.status = "failed"
            queue_item.error_detail = str(e)
            queue_item.save(update_fields=["status", "error_detail"])
            errors.append({"client_id": client_id, "error": str(e)})

    session.last_sync_at = timezone.now()
    session.save(update_fields=["last_sync_at"])

    return {"applied": applied, "conflicts": conflicts, "errors": errors}


def get_delta(user, device_id: str, since: str, entity_types: list) -> dict:
    """
    Return all server-side changes since `since` timestamp for given entity_types.
    Used by client after upload to pull down latest state.
    """
    from django.utils.dateparse import parse_datetime
    delta = {}
    since_dt = parse_datetime(since) if since else None

    for entity_type in entity_types:
        if entity_type not in ENTITY_REGISTRY:
            continue
        model, serializer_class = ENTITY_REGISTRY[entity_type]
        qs = model.objects.filter(
            **_user_filter(user, model)
        )
        if since_dt:
            qs = qs.filter(updated_at__gt=since_dt)
        delta[entity_type] = serializer_class(qs, many=True).data

    return {"delta": delta, "server_time": timezone.now().isoformat()}


def _apply_operation(user, item: SyncQueue, session: SyncSession):
    entity_type = item.entity_type
    if entity_type not in ENTITY_REGISTRY:
        raise ValueError(f"Unknown entity_type: {entity_type}")

    model, serializer_class = ENTITY_REGISTRY[entity_type]

    if item.operation == "create":
        ser = serializer_class(data=item.payload, context={"user": user})
        ser.is_valid(raise_exception=True)
        obj = ser.save()
        return str(obj.pk)

    elif item.operation == "update":
        obj = model.objects.get(pk=item.entity_id)
        # Conflict check
        if hasattr(obj, "updated_at") and session.last_sync_at:
            if obj.updated_at > session.last_sync_at:
                from rest_framework.serializers import Serializer
                raise ConflictError(server_version=serializer_class(obj).data)
        ser = serializer_class(obj, data=item.payload, partial=True, context={"user": user})
        ser.is_valid(raise_exception=True)
        ser.save()
        return str(obj.pk)

    elif item.operation == "delete":
        model.objects.filter(pk=item.entity_id).update(is_deleted=True)
        return item.entity_id

    raise ValueError(f"Unknown operation: {item.operation}")


def _user_filter(user, model) -> dict:
    """Best-effort ownership filter — extend per model as needed."""
    return {}


class ConflictError(Exception):
    def __init__(self, server_version: dict):
        self.server_version = server_version
        super().__init__("Sync conflict detected")
