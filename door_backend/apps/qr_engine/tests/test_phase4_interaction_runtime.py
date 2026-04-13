from rest_framework import status
from rest_framework.test import APITestCase

from apps.auth_identity.models import User
from apps.notifications.models import Notification
from apps.organizations.models import Group, GroupMember, Organization, OrganizationMember
from apps.qr_engine.models import (
    InteractionTemplate,
    NotificationRule,
    QRCode,
    QROwnerMember,
    TemplateAction,
    TemplateWorkflowState,
)


class InteractionRuntimeApiTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            email="owner-phase4@example.com",
            phone_number="+15550040001",
            full_name="Owner Phase4",
            password="pass1234",
        )
        self.manager = User.objects.create_user(
            email="manager-phase4@example.com",
            phone_number="+15550040002",
            full_name="Manager Phase4",
            password="pass1234",
        )
        self.backup = User.objects.create_user(
            email="backup-phase4@example.com",
            phone_number="+15550040003",
            full_name="Backup Phase4",
            password="pass1234",
        )
        self.family_member = User.objects.create_user(
            email="family-phase4@example.com",
            phone_number="+15550040004",
            full_name="Family Phase4",
            password="pass1234",
        )
        self.scanner = User.objects.create_user(
            email="scanner-phase4@example.com",
            phone_number="+15550040005",
            full_name="Scanner Phase4",
            password="pass1234",
        )

        self.organization = Organization.objects.create(
            name="Door Runtime Org",
            slug="door-runtime-org",
            owner=self.owner,
            created_by=self.owner,
        )
        OrganizationMember.objects.create(
            organization=self.organization,
            user=self.owner,
            role="owner",
        )
        OrganizationMember.objects.create(
            organization=self.organization,
            user=self.manager,
            role="manager",
        )

        self.group = Group.objects.create(
            organization=self.organization,
            name="Family Team",
            group_type="family",
            leader=self.manager,
        )
        GroupMember.objects.create(
            group=self.group,
            user=self.manager,
            role="group_leader",
        )
        GroupMember.objects.create(
            group=self.group,
            user=self.family_member,
            role="member",
        )

        self.template = InteractionTemplate.objects.create(
            name="Visitor Runtime",
            category="visitor_log",
            description="Visitor intake runtime flow",
            icon="door",
            schema_json={"pack": "visitor", "version": 1},
        )
        self.initial_state = TemplateWorkflowState.objects.create(
            template=self.template,
            state_name="Pending Review",
            state_type="pending",
            order=1,
            color="#ffaa33",
            is_initial=True,
        )
        self.approved_state = TemplateWorkflowState.objects.create(
            template=self.template,
            state_name="Approved",
            state_type="approved",
            order=2,
            color="#22aa55",
            is_final=True,
        )
        self.approve_action = TemplateAction.objects.create(
            template=self.template,
            action_name="Approve",
            action_key="approve",
            source_state=self.initial_state,
            target_state=self.approved_state,
            role_required="manager",
            button_style="primary",
            action_config_json={"notify_trigger": "interaction.transitioned"},
        )

        NotificationRule.objects.create(
            template=self.template,
            trigger_event="interaction.created",
            audience_type="owner",
            audience_config={},
            channel="in_app",
            priority="high",
        )
        NotificationRule.objects.create(
            template=self.template,
            trigger_event="interaction.created",
            audience_type="manager",
            audience_config={},
            channel="in_app",
            priority="high",
        )
        NotificationRule.objects.create(
            template=self.template,
            trigger_event="interaction.created",
            audience_type="backup_member",
            audience_config={},
            channel="in_app",
            priority="normal",
            fallback_rule_json={"channel": "push"},
        )
        NotificationRule.objects.create(
            template=self.template,
            trigger_event="interaction.created",
            audience_type="linked_group",
            audience_config={"include_roles": ["group_leader", "member"]},
            channel="in_app",
            priority="normal",
        )

        self.qr_code = QRCode.objects.create(
            organization=self.organization,
            group=self.group,
            label="Visitor Front Door",
            entity_type="organization",
            mode="custom_action",
            owner_type="organization",
            owner_id=str(self.organization.id),
            template=self.template,
            purpose="visitor_arrival",
            created_by=self.owner,
        )
        QROwnerMember.objects.create(
            qr_code=self.qr_code,
            owner=self.owner,
            member_user=self.backup,
            display_name="Backup Member",
            email=self.backup.email,
            phone=self.backup.phone_number,
            member_type="family",
            notify_role="bcc",
            priority=2,
            can_respond=True,
        )

    def test_scan_creates_interaction_record_and_initial_audit_log(self):
        self.client.force_authenticate(self.scanner)

        response = self.client.post(
            "/api/v1/qr/scan/",
            {
                "qr_code_id": str(self.qr_code.id),
                "device_id": "scanner-runtime-1",
                "metadata": {"visitor_name": "Amina"},
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["interaction_id"])
        self.assertEqual(response.data["interaction_status"], "open")
        self.assertEqual(response.data["interaction_state"]["id"], str(self.initial_state.id))

        detail_response = self.client.get(f"/api/v1/qr/interactions/{response.data['interaction_id']}/")
        self.assertEqual(detail_response.status_code, status.HTTP_200_OK)
        self.assertEqual(str(detail_response.data["template"]), str(self.template.id))
        self.assertEqual(detail_response.data["current_state"]["id"], str(self.initial_state.id))
        self.assertEqual(detail_response.data["payload_json"]["scan_metadata"]["visitor_name"], "Amina")

        audit_response = self.client.get(
            f"/api/v1/qr/interactions/{response.data['interaction_id']}/audit-logs/"
        )
        self.assertEqual(audit_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(audit_response.data), 1)
        self.assertEqual(audit_response.data[0]["action"], "interaction.created")
        self.assertEqual(audit_response.data[0]["to_state"]["id"], str(self.initial_state.id))

    def test_scan_routes_in_app_notifications_to_owner_manager_backup_and_linked_group(self):
        self.client.force_authenticate(self.scanner)

        response = self.client.post(
            "/api/v1/qr/scan/",
            {
                "qr_code_id": str(self.qr_code.id),
                "device_id": "scanner-runtime-2",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        recipients = set(
            Notification.objects.filter(
                source_entity_type="interaction_record",
                source_entity_id=response.data["interaction_id"],
            ).values_list("user__email", flat=True)
        )
        self.assertEqual(
            recipients,
            {
                self.owner.email,
                self.manager.email,
                self.backup.email,
                self.family_member.email,
            },
        )

    def test_interaction_action_endpoint_transitions_state_and_adds_audit_log(self):
        self.client.force_authenticate(self.scanner)
        create_response = self.client.post(
            "/api/v1/qr/scan/",
            {
                "qr_code_id": str(self.qr_code.id),
                "device_id": "scanner-runtime-3",
            },
            format="json",
        )
        interaction_id = create_response.data["interaction_id"]

        self.client.force_authenticate(self.manager)
        action_response = self.client.post(
            f"/api/v1/qr/interactions/{interaction_id}/actions/",
            {
                "action_key": "approve",
                "device_id": "manager-console-1",
                "payload_json": {"decision_note": "Approved at reception"},
            },
            format="json",
        )

        self.assertEqual(action_response.status_code, status.HTTP_200_OK)
        self.assertEqual(action_response.data["status"], "completed")
        self.assertEqual(action_response.data["current_state"]["id"], str(self.approved_state.id))

        audit_response = self.client.get(f"/api/v1/qr/interactions/{interaction_id}/audit-logs/")
        self.assertEqual(len(audit_response.data), 2)
        self.assertEqual(audit_response.data[-1]["action"], "approve")
        self.assertEqual(audit_response.data[-1]["from_state"]["id"], str(self.initial_state.id))
        self.assertEqual(audit_response.data[-1]["to_state"]["id"], str(self.approved_state.id))
