from rest_framework import status
from rest_framework.test import APITestCase

from apps.auth_identity.models import User
from apps.organizations.models import Organization, OrganizationMember
from apps.qr_engine.models import InteractionTemplate, QRCode


class DynamicQrTemplateApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="qr-owner@example.com",
            phone_number="+15550030001",
            full_name="QR Owner",
            password="pass1234",
        )
        self.org = Organization.objects.create(
            name="Door Org",
            slug="door-org-phase3",
            owner=self.user,
            created_by=self.user,
        )
        OrganizationMember.objects.create(
            organization=self.org,
            user=self.user,
            role="owner",
        )
        self.client.force_authenticate(self.user)

    def test_create_interaction_template_with_dynamic_schema(self):
        response = self.client.post(
            "/api/v1/qr/templates/",
            {
                "name": "Queue Intake",
                "category": "queue",
                "description": "Reusable queue intake template",
                "icon": "ticket",
                "default_language": "en",
                "is_public": False,
                "supports_offline": True,
                "version": 1,
                "schema_json": {
                    "pack": "queue",
                    "fields": ["full_name", "phone_number"],
                },
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["category"], "queue")
        self.assertEqual(response.data["schema_json"]["pack"], "queue")

    def test_create_template_field_workflow_action_and_notification_rule(self):
        template = InteractionTemplate.objects.create(
            name="Doorbell",
            category="doorbell",
            description="Door response workflow",
            icon="bell",
            schema_json={"pack": "doorbell"},
        )

        field_response = self.client.post(
            "/api/v1/qr/template-fields/",
            {
                "template": str(template.id),
                "field_key": "visitor_name",
                "label": "Visitor name",
                "field_type": "text",
                "is_required": True,
                "default_value": "",
                "options_json": {},
                "validation_json": {"max_length": 120},
                "visibility_rule_json": {},
            },
            format="json",
        )
        self.assertEqual(field_response.status_code, status.HTTP_201_CREATED)

        state_response = self.client.post(
            "/api/v1/qr/template-workflow-states/",
            {
                "template": str(template.id),
                "state_name": "Pending",
                "state_type": "pending",
                "order": 1,
                "color": "#f6b94a",
                "is_initial": True,
                "is_final": False,
            },
            format="json",
        )
        self.assertEqual(state_response.status_code, status.HTTP_201_CREATED)

        action_response = self.client.post(
            "/api/v1/qr/template-actions/",
            {
                "template": str(template.id),
                "action_name": "Acknowledge",
                "action_key": "acknowledge",
                "source_state": state_response.data["id"],
                "target_state": state_response.data["id"],
                "role_required": "staff",
                "button_style": "primary",
                "action_config_json": {"notify": True},
            },
            format="json",
        )
        self.assertEqual(action_response.status_code, status.HTTP_201_CREATED)

        rule_response = self.client.post(
            "/api/v1/qr/notification-rules/",
            {
                "template": str(template.id),
                "trigger_event": "scan.created",
                "audience_type": "organization_role",
                "audience_config": {"roles": ["owner", "staff"]},
                "channel": "in_app",
                "priority": "high",
                "fallback_rule_json": {"channel": "email"},
            },
            format="json",
        )
        self.assertEqual(rule_response.status_code, status.HTTP_201_CREATED)

    def test_create_qr_code_is_tied_to_template_and_generates_qr_token(self):
        template = InteractionTemplate.objects.create(
            name="Expo Booth Visitor",
            category="expo_booth_visitor",
            description="Lead capture flow",
            icon="badge",
            schema_json={"pack": "expo"},
        )

        response = self.client.post(
            "/api/v1/qr/codes/",
            {
                "organization": str(self.org.id),
                "name": "Expo Booth A",
                "owner_type": "organization",
                "owner_id": str(self.org.id),
                "template": str(template.id),
                "purpose": "lead_capture",
                "status": "active",
                "expiry": None,
                "metadata_json": {"booth": "A"},
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(str(response.data["template"]), str(template.id))
        self.assertEqual(response.data["purpose"], "lead_capture")
        self.assertTrue(response.data["qr_token"])

    def test_scan_response_is_template_driven_not_queue_only(self):
        template = InteractionTemplate.objects.create(
            name="Wedding Guest Check-in",
            category="wedding_guest_check_in",
            description="Guest arrival flow",
            icon="heart",
            schema_json={"pack": "wedding", "workflow": "guest_arrival"},
        )
        qr_code = QRCode.objects.create(
            organization=self.org,
            label="Wedding Entrance",
            entity_type="organization",
            mode="custom_action",
            created_by=self.user,
            owner_type="organization",
            owner_id=str(self.org.id),
            template=template,
            purpose="guest_check_in",
            qr_token="wedding-entrance",
            metadata_json={"lane": "main"},
        )

        self.client.force_authenticate(self.user)
        response = self.client.post(
            "/api/v1/qr/scan/",
            {
                "qr_code_id": str(qr_code.id),
                "device_id": "scanner-1",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["template"]["id"], str(template.id))
        self.assertEqual(response.data["template"]["category"], "wedding_guest_check_in")
        self.assertEqual(response.data["purpose"], "guest_check_in")
