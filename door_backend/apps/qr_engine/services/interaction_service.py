from django.db import transaction

from apps.notifications.services.notification_service import NotificationService
from apps.organizations.models import GroupMember, OrganizationMember
from apps.qr_engine.models import (
    InteractionAuditLog,
    InteractionRecord,
    NotificationRule,
    QROwnerMember,
    TemplateAction,
    TemplateWorkflowState,
)
from apps.qr_engine.services.pack_runtime_service import TemplatePackRuntimeService


class InteractionRuntimeService:
    @staticmethod
    def _initial_state_for_template(template):
        return (
            template.workflow_states.filter(is_initial=True).order_by("order", "created_at_server").first()
            or template.workflow_states.order_by("order", "created_at_server").first()
        )

    @staticmethod
    def _status_for_state(state):
        if state and state.is_final:
            return "completed"
        return "open"

    @staticmethod
    def _serialize_state(state):
        if not state:
            return None
        return {
            "id": str(state.id),
            "state_name": state.state_name,
            "state_type": state.state_type,
            "is_initial": state.is_initial,
            "is_final": state.is_final,
        }

    @classmethod
    def _resolve_recipients(cls, *, interaction, rule: NotificationRule):
        qr_entity = interaction.qr_entity
        recipients = {}

        def add_user(user):
            if user and getattr(user, "id", None):
                recipients[str(user.id)] = user

        if rule.audience_type == "owner":
            add_user(qr_entity.created_by)
            if qr_entity.organization_id:
                add_user(qr_entity.organization.owner)

        elif rule.audience_type == "manager" and qr_entity.organization_id:
            memberships = OrganizationMember.objects.filter(
                organization=qr_entity.organization,
                membership_status="active",
                role__in=["manager", "organization_admin"],
            ).select_related("user")
            for membership in memberships:
                add_user(membership.user)

        elif rule.audience_type == "backup_member":
            backup_members = (
                QROwnerMember.objects.filter(
                    qr_code=qr_entity,
                    is_active=True,
                    can_respond=True,
                    member_user__isnull=False,
                )
                .exclude(notify_role="to")
                .select_related("member_user")
            )
            for member in backup_members:
                add_user(member.member_user)

        elif rule.audience_type == "linked_group" and qr_entity.group_id:
            include_roles = rule.audience_config.get("include_roles") or []
            memberships = GroupMember.objects.filter(
                group=qr_entity.group,
                membership_status="active",
            ).select_related("user")
            if include_roles:
                memberships = memberships.filter(role__in=include_roles)
            for membership in memberships:
                add_user(membership.user)

        elif rule.audience_type == "organization_role" and qr_entity.organization_id:
            roles = rule.audience_config.get("roles") or []
            memberships = OrganizationMember.objects.filter(
                organization=qr_entity.organization,
                membership_status="active",
            ).select_related("user")
            if roles:
                memberships = memberships.filter(role__in=roles)
            for membership in memberships:
                add_user(membership.user)

        return list(recipients.values())

    @classmethod
    def _notify(cls, *, interaction: InteractionRecord, trigger_event: str):
        rules = NotificationRule.objects.filter(
            template=interaction.template,
            trigger_event=trigger_event,
            channel="in_app",
        )
        for rule in rules:
            recipients = cls._resolve_recipients(interaction=interaction, rule=rule)
            for recipient in recipients:
                NotificationService.create(
                    user=recipient,
                    notif_type="system",
                    title=f"Interaction update: {interaction.qr_entity.label}",
                    body=f"{interaction.template.name} triggered {trigger_event}.",
                    organization=interaction.qr_entity.organization,
                    data={
                        "interaction_id": str(interaction.id),
                        "template_id": str(interaction.template_id),
                        "trigger_event": trigger_event,
                        "current_state": cls._serialize_state(interaction.current_state),
                        "fallback_rule": rule.fallback_rule_json,
                        "channel": rule.channel,
                    },
                    source_entity_type="interaction_record",
                    source_entity_id=str(interaction.id),
                    priority=rule.priority,
                )

    @classmethod
    def create_from_scan(cls, *, scan):
        template = scan.qr_code.template
        if not template:
            return None

        current_state = cls._initial_state_for_template(template)
        interaction = InteractionRecord.objects.create(
            template=template,
            qr_entity=scan.qr_code,
            scan=scan,
            initiated_by=scan.scanned_by,
            initiated_at=scan.scanned_at,
            current_state=current_state,
            payload_json={
                "scan_id": str(scan.id),
                "qr_entity_id": str(scan.qr_code_id),
                "template_snapshot": scan.template_snapshot,
                "scan_metadata": scan.metadata,
                "action_payload": scan.action_payload,
            },
            status=cls._status_for_state(current_state),
        )
        InteractionAuditLog.objects.create(
            interaction=interaction,
            actor=scan.scanned_by,
            action="interaction.created",
            to_state=current_state,
            snapshot_json={
                "template_id": str(template.id),
                "qr_entity_id": str(scan.qr_code_id),
                "payload_json": interaction.payload_json,
            },
            device_id=scan.device_id,
            created_at_client=scan.created_at_client,
        )
        interaction = TemplatePackRuntimeService.on_interaction_created(interaction=interaction)
        cls._notify(interaction=interaction, trigger_event="interaction.created")
        return interaction

    @classmethod
    def actor_roles(cls, *, interaction: InteractionRecord, actor):
        if not actor or not getattr(actor, "id", None):
            return set()

        roles = set()
        qr_entity = interaction.qr_entity
        if qr_entity.organization_id:
            memberships = OrganizationMember.objects.filter(
                organization=qr_entity.organization,
                user=actor,
                membership_status="active",
            ).values_list("role", flat=True)
            roles.update(memberships)
            if qr_entity.organization.owner_id == actor.id:
                roles.add("owner")

        if qr_entity.group_id:
            memberships = GroupMember.objects.filter(
                group=qr_entity.group,
                user=actor,
                membership_status="active",
            ).values_list("role", flat=True)
            roles.update(memberships)
            if qr_entity.group.leader_id == actor.id:
                roles.add("group_leader")

        return roles

    @classmethod
    @transaction.atomic
    def apply_action(cls, *, interaction: InteractionRecord, action_key: str, actor=None, device_id="", payload_json=None):
        template_action = TemplateAction.objects.select_related("source_state", "target_state").get(
            template=interaction.template,
            action_key=action_key,
        )

        actor_roles = cls.actor_roles(interaction=interaction, actor=actor)
        if template_action.role_required:
            allowed_roles = {template_action.role_required}
            if template_action.role_required == "manager":
                allowed_roles.update({"owner", "organization_admin"})
            if actor_roles.isdisjoint(allowed_roles):
                raise PermissionError("Actor does not have the required interaction role.")

        if template_action.source_state_id and interaction.current_state_id != template_action.source_state_id:
            raise ValueError("Action is not allowed from the current state.")

        previous_state = interaction.current_state
        next_state = template_action.target_state or previous_state
        payload_json = payload_json or {}

        interaction.current_state = next_state
        interaction.status = "completed" if next_state and next_state.is_final else "in_progress"
        interaction.payload_json = {
            **interaction.payload_json,
            "last_action": {
                "action_key": template_action.action_key,
                "payload_json": payload_json,
            },
        }
        if device_id:
            interaction.last_modified_by_device_id = device_id
        interaction.version += 1
        interaction.save(
            update_fields=[
                "current_state",
                "status",
                "payload_json",
                "last_modified_by_device_id",
                "version",
                "updated_at_server",
            ]
        )

        InteractionAuditLog.objects.create(
            interaction=interaction,
            actor=actor,
            action=template_action.action_key,
            from_state=previous_state,
            to_state=next_state,
            snapshot_json={
                "template_action": template_action.action_name,
                "payload_json": payload_json,
                "status": interaction.status,
            },
            device_id=device_id,
        )
        interaction = TemplatePackRuntimeService.on_interaction_action(
            interaction=interaction,
            action_key=template_action.action_key,
            actor=actor,
            actor_device_id=device_id,
            payload_json=payload_json,
        )
        cls._notify(
            interaction=interaction,
            trigger_event=template_action.action_config_json.get("notify_trigger", "interaction.updated"),
        )
        return interaction
