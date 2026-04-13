from django.utils import timezone

from apps.qr_engine.models import InteractionAuditLog
from apps.queue_control.models import QueueSession, QueueTicket
from apps.queue_control.services.action_service import QueueActionService
from apps.queue_control.services.ticket_service import QueueTicketService

from .template_pack_service import TemplatePackService


class TemplatePackRuntimeService:
    @staticmethod
    def _serialize_interaction(interaction):
        return {
            "id": str(interaction.id),
            "status": interaction.status,
            "current_state": {
                "id": str(interaction.current_state.id),
                "state_name": interaction.current_state.state_name,
                "state_type": interaction.current_state.state_type,
            } if interaction.current_state_id else None,
            "payload_json": interaction.payload_json,
        }

    @staticmethod
    def _serialize_ticket(ticket):
        return {
            "id": str(ticket.id),
            "queue": str(ticket.queue_id),
            "session": str(ticket.session_id) if ticket.session_id else None,
            "number": ticket.number,
            "status": ticket.status,
            "called_at": ticket.called_at.isoformat() if ticket.called_at else None,
            "recalled_at": ticket.recalled_at.isoformat() if ticket.recalled_at else None,
            "completed_at": ticket.completed_at.isoformat() if ticket.completed_at else None,
        }

    @staticmethod
    def _state(template, state_type: str):
        if not template:
            return None
        return template.workflow_states.filter(state_type=state_type).first()

    @staticmethod
    def _queue_ticket_for_interaction(interaction):
        ticket_id = ((interaction.payload_json or {}).get("queue_ticket") or {}).get("id")
        if not ticket_id:
            return None
        return QueueTicket.objects.filter(pk=ticket_id).first()

    @classmethod
    def on_interaction_created(cls, *, interaction):
        pack_key = TemplatePackService.get_pack_key(interaction.template)
        payload_json = dict(interaction.payload_json or {})
        scan_metadata = payload_json.get("scan_metadata", {})

        if pack_key == "queue_token" and interaction.qr_entity.queue_id:
            session = (
                interaction.qr_entity.queue.sessions.filter(status="active")
                .order_by("-started_at")
                .first()
            )
            if session is None:
                session = QueueSession.objects.create(
                    queue=interaction.qr_entity.queue,
                    started_by=interaction.initiated_by,
                    status="active",
                )
            ticket = QueueTicketService.issue_ticket(
                queue=interaction.qr_entity.queue,
                session=session,
                user=interaction.initiated_by,
                device_id=interaction.scan.device_id if interaction.scan_id else "",
            )
            payload_json["queue_ticket"] = {
                "id": str(ticket.id),
                "number": ticket.number,
                "status": ticket.status,
                "queue_id": str(ticket.queue_id),
            }
            issued_state = cls._state(interaction.template, "issued")
            if issued_state:
                interaction.current_state = issued_state

        elif pack_key == "doorbell_visitor_contact":
            payload_json["visitor_contact"] = {
                "visitor_name": scan_metadata.get("visitor_name") or scan_metadata.get("name") or "",
                "message": scan_metadata.get("message", ""),
                "future_media_supported": {"photo": False, "voice": False},
            }

        elif pack_key == "visitor_log":
            payload_json["check_in_record"] = {
                "name": scan_metadata.get("name") or scan_metadata.get("visitor_name") or "",
                "purpose": scan_metadata.get("purpose", ""),
                "checked_in_at": interaction.initiated_at.isoformat(),
                "history_enabled": True,
            }

        interaction.payload_json = payload_json
        interaction.save(update_fields=["payload_json", "current_state", "updated_at_server"])
        return interaction

    @classmethod
    def on_interaction_action(cls, *, interaction, action_key: str, actor=None, actor_device_id: str = "", payload_json=None):
        pack_key = TemplatePackService.get_pack_key(interaction.template)
        if pack_key != "queue_token":
            return interaction

        ticket = cls._queue_ticket_for_interaction(interaction)
        if not ticket:
            return interaction

        action_map = {
            "call": "call",
            "skip": "skip",
            "recall": "recall",
            "complete": "complete",
        }
        if action_key not in action_map:
            return interaction

        ticket = QueueActionService.transition_ticket(
            ticket=ticket,
            action=action_map[action_key],
            actor=actor,
            actor_device_id=actor_device_id,
        )
        if action_key == "call":
            interaction.qr_entity.queue.current_serving = ticket.number
            interaction.qr_entity.queue.save(update_fields=["current_serving"])

        updated_payload = dict(interaction.payload_json or {})
        updated_payload["queue_ticket"] = {
            "id": str(ticket.id),
            "number": ticket.number,
            "status": ticket.status,
            "queue_id": str(ticket.queue_id),
        }
        interaction.payload_json = updated_payload
        interaction.save(update_fields=["payload_json", "updated_at_server"])
        return interaction

    @classmethod
    def execute_qr_runtime_action(cls, *, qr_code, operation: str, actor=None, actor_device_id: str = ""):
        pack_key = TemplatePackService.get_pack_key(qr_code.template)
        if pack_key != "queue_token":
            raise ValueError("Runtime action is not supported for this pack.")
        if operation != "next":
            raise ValueError("Unsupported runtime operation.")

        candidates = []
        for interaction in qr_code.interaction_records.select_related("template", "current_state").all().order_by("initiated_at"):
            ticket = cls._queue_ticket_for_interaction(interaction)
            if ticket and ticket.status in {"issued", "waiting", "recalled"}:
                candidates.append((interaction, ticket))

        if not candidates:
            raise ValueError("No waiting queue interactions available.")

        interaction, ticket = candidates[0]
        before_state = interaction.current_state
        ticket = QueueActionService.transition_ticket(
            ticket=ticket,
            action="call",
            actor=actor,
            actor_device_id=actor_device_id,
        )
        qr_code.queue.current_serving = ticket.number
        qr_code.queue.save(update_fields=["current_serving"])

        called_state = cls._state(interaction.template, "called")
        interaction.current_state = called_state or interaction.current_state
        interaction.status = "in_progress"
        interaction.payload_json = {
            **(interaction.payload_json or {}),
            "queue_ticket": {
                "id": str(ticket.id),
                "number": ticket.number,
                "status": ticket.status,
                "queue_id": str(ticket.queue_id),
            },
        }
        interaction.version += 1
        interaction.last_modified_by_device_id = actor_device_id
        interaction.save(
            update_fields=[
                "current_state",
                "status",
                "payload_json",
                "version",
                "last_modified_by_device_id",
                "updated_at_server",
            ]
        )
        InteractionAuditLog.objects.create(
            interaction=interaction,
            actor=actor,
            action="next",
            from_state=before_state,
            to_state=interaction.current_state,
            snapshot_json={"queue_ticket_status": ticket.status, "queue_ticket_number": ticket.number},
            device_id=actor_device_id,
            created_at_client=timezone.now(),
        )
        return {
            "interaction": cls._serialize_interaction(interaction),
            "ticket": cls._serialize_ticket(ticket),
        }
