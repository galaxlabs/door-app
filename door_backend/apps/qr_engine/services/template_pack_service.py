from copy import deepcopy

from apps.qr_engine.models import (
    InteractionTemplate,
    NotificationRule,
    QRCode,
    QROwnerMember,
    TemplateAction,
    TemplateField,
    TemplateWorkflowState,
)
from apps.qr_engine.services.template_service import QRTemplateService


PACK_DEFINITIONS = {
    "queue_token": {
        "pack_key": "queue_token",
        "name": "Queue / Token Pack",
        "category": "queue",
        "description": "Reusable queue token and serving workflow.",
        "icon": "ticket",
        "default_language": "en",
        "is_public": False,
        "supports_offline": True,
        "schema_json": {
            "pack_key": "queue_token",
            "configurable": True,
            "runtime_behavior": {"scan_create": "issue_queue_token", "qr_actions": ["next"]},
            "admin_setup_flow": [
                "Select organization and queue",
                "Review token and service settings",
                "Create QR code and print token sign",
            ],
            "minimal_ui_requirements": [
                "Queue pack picker with queue selector",
                "Token display with current ticket number",
                "Operator controls for next, call, skip, recall, and complete",
            ],
        },
        "fields": [
            {
                "field_key": "customer_name",
                "label": "Customer name",
                "field_type": "text",
                "is_required": False,
                "default_value": "",
                "options_json": {},
                "validation_json": {"max_length": 120},
                "visibility_rule_json": {},
            },
            {
                "field_key": "service_note",
                "label": "Service note",
                "field_type": "textarea",
                "is_required": False,
                "default_value": "",
                "options_json": {},
                "validation_json": {"max_length": 500},
                "visibility_rule_json": {},
            },
        ],
        "workflow_states": [
            {"state_name": "Issued", "state_type": "issued", "order": 1, "color": "#5a8fef", "is_initial": True, "is_final": False},
            {"state_name": "Called", "state_type": "called", "order": 2, "color": "#f3b14a", "is_initial": False, "is_final": False},
            {"state_name": "Skipped", "state_type": "skipped", "order": 3, "color": "#d97b7b", "is_initial": False, "is_final": False},
            {"state_name": "Recalled", "state_type": "recalled", "order": 4, "color": "#8c72d9", "is_initial": False, "is_final": False},
            {"state_name": "Completed", "state_type": "completed", "order": 5, "color": "#3ca66b", "is_initial": False, "is_final": True},
        ],
        "actions": [
            {"action_name": "Next", "action_key": "next", "source_state": None, "target_state": "called", "role_required": "manager", "button_style": "primary", "action_config_json": {"runtime_operation": "next", "scope": "qr_code"}},
            {"action_name": "Call", "action_key": "call", "source_state": "issued", "target_state": "called", "role_required": "manager", "button_style": "primary", "action_config_json": {"runtime_operation": "call"}},
            {"action_name": "Skip", "action_key": "skip", "source_state": "called", "target_state": "skipped", "role_required": "manager", "button_style": "secondary", "action_config_json": {"runtime_operation": "skip"}},
            {"action_name": "Recall", "action_key": "recall", "source_state": "skipped", "target_state": "recalled", "role_required": "manager", "button_style": "secondary", "action_config_json": {"runtime_operation": "recall"}},
            {"action_name": "Complete", "action_key": "complete", "source_state": "called", "target_state": "completed", "role_required": "manager", "button_style": "success", "action_config_json": {"runtime_operation": "complete"}},
        ],
        "notification_rules": [
            {"trigger_event": "interaction.created", "audience_type": "owner", "audience_config": {}, "channel": "in_app", "priority": "high", "fallback_rule_json": {}},
            {"trigger_event": "interaction.created", "audience_type": "manager", "audience_config": {}, "channel": "in_app", "priority": "high", "fallback_rule_json": {}},
        ],
    },
    "doorbell_visitor_contact": {
        "pack_key": "doorbell_visitor_contact",
        "name": "Doorbell / Visitor Contact Pack",
        "category": "doorbell",
        "description": "Visitor contact flow for notifying owner and backup members.",
        "icon": "bell",
        "default_language": "en",
        "is_public": False,
        "supports_offline": True,
        "schema_json": {
            "pack_key": "doorbell_visitor_contact",
            "configurable": True,
            "runtime_behavior": {"scan_create": "capture_visitor_contact"},
            "future_fields": ["photo", "voice"],
            "admin_setup_flow": [
                "Select organization and owner",
                "Add backup members",
                "Publish QR code for front door use",
            ],
            "minimal_ui_requirements": [
                "Visitor name field",
                "Optional message field",
                "Owner and backup notification summary",
            ],
        },
        "fields": [
            {"field_key": "visitor_name", "label": "Visitor name", "field_type": "text", "is_required": True, "default_value": "", "options_json": {}, "validation_json": {"max_length": 120}, "visibility_rule_json": {}},
            {"field_key": "message", "label": "Message", "field_type": "textarea", "is_required": False, "default_value": "", "options_json": {}, "validation_json": {"max_length": 500}, "visibility_rule_json": {}},
        ],
        "workflow_states": [
            {"state_name": "Pending", "state_type": "pending", "order": 1, "color": "#f3b14a", "is_initial": True, "is_final": False},
            {"state_name": "Acknowledged", "state_type": "acknowledged", "order": 2, "color": "#5a8fef", "is_initial": False, "is_final": False},
            {"state_name": "Resolved", "state_type": "resolved", "order": 3, "color": "#3ca66b", "is_initial": False, "is_final": True},
        ],
        "actions": [
            {"action_name": "Acknowledge", "action_key": "acknowledge", "source_state": "pending", "target_state": "acknowledged", "role_required": "manager", "button_style": "primary", "action_config_json": {}},
            {"action_name": "Resolve", "action_key": "resolve", "source_state": "acknowledged", "target_state": "resolved", "role_required": "manager", "button_style": "success", "action_config_json": {}},
        ],
        "notification_rules": [
            {"trigger_event": "interaction.created", "audience_type": "owner", "audience_config": {}, "channel": "in_app", "priority": "high", "fallback_rule_json": {}},
            {"trigger_event": "interaction.created", "audience_type": "manager", "audience_config": {}, "channel": "in_app", "priority": "normal", "fallback_rule_json": {}},
            {"trigger_event": "interaction.created", "audience_type": "backup_member", "audience_config": {}, "channel": "in_app", "priority": "high", "fallback_rule_json": {"channel": "push"}},
        ],
    },
    "visitor_log": {
        "pack_key": "visitor_log",
        "name": "Visitor Log Pack",
        "category": "visitor_log",
        "description": "Check-in flow for visitor history and purpose tracking.",
        "icon": "book-open",
        "default_language": "en",
        "is_public": False,
        "supports_offline": True,
        "schema_json": {
            "pack_key": "visitor_log",
            "configurable": True,
            "runtime_behavior": {"scan_create": "capture_check_in_record"},
            "admin_setup_flow": [
                "Select organization and entry point",
                "Choose visitor fields and review history settings",
                "Publish QR code for visitor check-in",
            ],
            "minimal_ui_requirements": [
                "Visitor name and purpose form",
                "Recent visitor history list",
                "Check-in timestamp and status display",
            ],
        },
        "fields": [
            {"field_key": "name", "label": "Name", "field_type": "text", "is_required": True, "default_value": "", "options_json": {}, "validation_json": {"max_length": 120}, "visibility_rule_json": {}},
            {"field_key": "purpose", "label": "Purpose", "field_type": "text", "is_required": True, "default_value": "", "options_json": {}, "validation_json": {"max_length": 255}, "visibility_rule_json": {}},
        ],
        "workflow_states": [
            {"state_name": "Checked In", "state_type": "checked_in", "order": 1, "color": "#5a8fef", "is_initial": True, "is_final": False},
            {"state_name": "Logged", "state_type": "logged", "order": 2, "color": "#3ca66b", "is_initial": False, "is_final": True},
        ],
        "actions": [
            {"action_name": "Complete Log", "action_key": "complete", "source_state": "checked_in", "target_state": "logged", "role_required": "manager", "button_style": "success", "action_config_json": {}},
        ],
        "notification_rules": [
            {"trigger_event": "interaction.created", "audience_type": "owner", "audience_config": {}, "channel": "in_app", "priority": "normal", "fallback_rule_json": {}},
            {"trigger_event": "interaction.created", "audience_type": "manager", "audience_config": {}, "channel": "in_app", "priority": "normal", "fallback_rule_json": {}},
        ],
    },
}


class TemplatePackService:
    @staticmethod
    def catalog():
        return [deepcopy(definition) for definition in PACK_DEFINITIONS.values()]

    @staticmethod
    def get_definition(pack_key: str):
        if pack_key not in PACK_DEFINITIONS:
            raise ValueError(f"Unknown template pack '{pack_key}'.")
        return deepcopy(PACK_DEFINITIONS[pack_key])

    @staticmethod
    def get_pack_key(template: InteractionTemplate | None) -> str:
        if not template:
            return ""
        return template.schema_json.get("pack_key", "")

    @classmethod
    def _existing_template(cls, pack_key: str):
        for template in InteractionTemplate.objects.all():
            if template.schema_json.get("pack_key") == pack_key:
                return template
        return None

    @classmethod
    def seed_pack(cls, pack_key: str) -> InteractionTemplate:
        definition = cls.get_definition(pack_key)
        template = cls._existing_template(pack_key)
        schema_json = {**definition["schema_json"], "pack_key": pack_key}
        if template is None:
            template = InteractionTemplate.objects.create(
                name=definition["name"],
                category=definition["category"],
                description=definition["description"],
                icon=definition["icon"],
                default_language=definition["default_language"],
                is_public=definition["is_public"],
                supports_offline=definition["supports_offline"],
                version=1,
                schema_json=schema_json,
            )
        else:
            template.name = definition["name"]
            template.category = definition["category"]
            template.description = definition["description"]
            template.icon = definition["icon"]
            template.default_language = definition["default_language"]
            template.is_public = definition["is_public"]
            template.supports_offline = definition["supports_offline"]
            template.schema_json = schema_json
            template.save()

        template.fields.all().delete()
        template.workflow_states.all().delete()
        template.actions.all().delete()
        template.notification_rules.all().delete()

        for field in definition["fields"]:
            TemplateField.objects.create(template=template, **field)

        states = {}
        for state in definition["workflow_states"]:
            state_obj = TemplateWorkflowState.objects.create(template=template, **state)
            states[state_obj.state_type] = state_obj

        for action in definition["actions"]:
            source_state = states.get(action["source_state"]) if action.get("source_state") else None
            target_state = states.get(action["target_state"]) if action.get("target_state") else None
            TemplateAction.objects.create(
                template=template,
                action_name=action["action_name"],
                action_key=action["action_key"],
                source_state=source_state,
                target_state=target_state,
                role_required=action["role_required"],
                button_style=action["button_style"],
                action_config_json=action["action_config_json"],
            )

        for rule in definition["notification_rules"]:
            NotificationRule.objects.create(template=template, **rule)

        return template

    @classmethod
    def seed_packs(cls, pack_keys: list[str]):
        return [cls.seed_pack(pack_key) for pack_key in pack_keys]

    @classmethod
    def admin_setup(
        cls,
        *,
        pack_key: str,
        created_by,
        name: str,
        organization=None,
        event=None,
        group=None,
        queue=None,
        owner_type: str = "",
        owner_id: str = "",
        metadata_json=None,
        owner_members=None,
    ):
        template = cls.seed_pack(pack_key)
        qr_code = QRTemplateService.create_qr_code(
            label=name,
            organization=organization,
            event=event,
            group=group,
            queue=queue,
            template=template,
            owner_type=owner_type or "organization",
            owner_id=owner_id,
            metadata_json=metadata_json or {},
            metadata=metadata_json or {},
            entity_type="queue" if queue else "organization",
            mode="custom_action",
            payload_type="custom_action",
            created_by=created_by,
        )

        created_members = []
        for member in owner_members or []:
            created_members.append(
                QROwnerMember.objects.create(
                    qr_code=qr_code,
                    owner=created_by,
                    member_user=member.get("member_user"),
                    display_name=member["display_name"],
                    phone=member.get("phone", ""),
                    email=member.get("email", ""),
                    member_type=member.get("member_type", "team"),
                    notify_role=member.get("notify_role", "to"),
                    priority=member.get("priority", 1),
                    can_respond=member.get("can_respond", True),
                    availability=member.get("availability", "available"),
                )
            )
        return template, qr_code, created_members
