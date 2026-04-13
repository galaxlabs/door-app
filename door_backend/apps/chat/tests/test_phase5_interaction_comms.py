from rest_framework import status
from rest_framework.test import APITestCase

from apps.auth_identity.models import User
from apps.broadcast.models import BroadcastDelivery
from apps.organizations.models import Group, GroupMember, Organization, OrganizationMember
from apps.qr_engine.models import (
    InteractionRecord,
    InteractionTemplate,
    QRCode,
    TemplateWorkflowState,
)


class InteractionCommunicationApiTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            email="owner-phase5@example.com",
            phone_number="+15550050001",
            full_name="Owner Phase5",
            password="pass1234",
        )
        self.manager = User.objects.create_user(
            email="manager-phase5@example.com",
            phone_number="+15550050002",
            full_name="Manager Phase5",
            password="pass1234",
        )
        self.member = User.objects.create_user(
            email="member-phase5@example.com",
            phone_number="+15550050003",
            full_name="Member Phase5",
            password="pass1234",
        )

        self.organization = Organization.objects.create(
            name="Door Comms Org",
            slug="door-comms-org",
            owner=self.owner,
            created_by=self.owner,
        )
        OrganizationMember.objects.create(organization=self.organization, user=self.owner, role="owner")
        OrganizationMember.objects.create(organization=self.organization, user=self.manager, role="manager")
        OrganizationMember.objects.create(organization=self.organization, user=self.member, role="member")

        self.group = Group.objects.create(
            organization=self.organization,
            name="Coordination Team",
            group_type="office_team",
            leader=self.manager,
        )
        GroupMember.objects.create(group=self.group, user=self.manager, role="group_leader")
        GroupMember.objects.create(group=self.group, user=self.member, role="member")

        self.template = InteractionTemplate.objects.create(
            name="Coordination Flow",
            category="event_coordination",
            schema_json={"pack": "coordination"},
        )
        self.initial_state = TemplateWorkflowState.objects.create(
            template=self.template,
            state_name="Open",
            state_type="open",
            order=1,
            is_initial=True,
        )
        self.qr_code = QRCode.objects.create(
            organization=self.organization,
            group=self.group,
            label="Ops QR",
            entity_type="organization",
            mode="custom_action",
            owner_type="organization",
            owner_id=str(self.organization.id),
            template=self.template,
            purpose="ops",
            created_by=self.owner,
        )
        self.interaction = InteractionRecord.objects.create(
            template=self.template,
            qr_entity=self.qr_code,
            initiated_by=self.owner,
            current_state=self.initial_state,
            payload_json={"kind": "phase5"},
            status="open",
        )

    def test_can_create_direct_chat_and_interaction_chat_and_send_message(self):
        self.client.force_authenticate(self.owner)

        direct_response = self.client.post(
            "/api/v1/chat/rooms/ensure-direct/",
            {"user_id": str(self.manager.id)},
            format="json",
        )
        self.assertEqual(direct_response.status_code, status.HTTP_200_OK)
        self.assertEqual(direct_response.data["type"], "direct")

        interaction_room_response = self.client.post(
            "/api/v1/chat/rooms/ensure-interaction/",
            {
                "interaction_id": str(self.interaction.id),
                "member_user_ids": [str(self.manager.id), str(self.member.id)],
            },
            format="json",
        )
        self.assertEqual(interaction_room_response.status_code, status.HTTP_200_OK)
        self.assertEqual(interaction_room_response.data["type"], "interaction")
        self.assertEqual(str(interaction_room_response.data["interaction"]), str(self.interaction.id))

        message_response = self.client.post(
            f"/api/v1/chat/rooms/{interaction_room_response.data['id']}/messages/",
            {
                "type": "text",
                "content": "Please coordinate on this interaction.",
                "client_id": "phase5-chat-1",
                "sender_device_id": "web-admin-1",
            },
            format="json",
        )
        self.assertEqual(message_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(message_response.data["delivery_state"], "sent")

        status_response = self.client.post(
            f"/api/v1/chat/messages/{message_response.data['id']}/status/",
            {
                "status": "seen",
                "status_device_id": "manager-phone-1",
            },
            format="json",
        )
        self.assertEqual(status_response.status_code, status.HTTP_200_OK)
        self.assertEqual(status_response.data["delivery_state"], "seen")

    def test_can_create_interaction_linked_broadcast_and_update_delivery_state(self):
        self.client.force_authenticate(self.owner)

        channel_response = self.client.post(
            "/api/v1/broadcast/channels/",
            {
                "organization": str(self.organization.id),
                "group": str(self.group.id),
                "interaction": str(self.interaction.id),
                "name": "Interaction Alerts",
                "description": "Phase 5 channel",
                "type": "private",
                "is_active": True,
            },
            format="json",
        )
        self.assertEqual(channel_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(str(channel_response.data["interaction"]), str(self.interaction.id))

        message_response = self.client.post(
            "/api/v1/broadcast/messages/",
            {
                "channel": str(channel_response.data["id"]),
                "interaction": str(self.interaction.id),
                "title": "Please assemble",
                "body": "Team coordination needed",
                "type": "alert",
                "target_mode": "group",
                "payload": {"template_id": str(self.template.id)},
            },
            format="json",
        )
        self.assertEqual(message_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(str(message_response.data["interaction"]), str(self.interaction.id))

        dispatch_response = self.client.post(
            f"/api/v1/broadcast/messages/{message_response.data['id']}/dispatch/",
            format="json",
        )
        self.assertEqual(dispatch_response.status_code, status.HTTP_200_OK)
        self.assertEqual(dispatch_response.data["status"], "sent")

        delivery = BroadcastDelivery.objects.filter(message_id=message_response.data["id"], user=self.member).first()
        self.assertIsNotNone(delivery)
        self.assertIn(delivery.status, {"sent", "delivered"})

        self.client.force_authenticate(self.member)
        delivery_response = self.client.post(
            f"/api/v1/broadcast/messages/{message_response.data['id']}/delivery-status/",
            {
                "delivery_id": str(delivery.id),
                "status": "seen",
            },
            format="json",
        )
        self.assertEqual(delivery_response.status_code, status.HTTP_200_OK)
        self.assertEqual(delivery_response.data["status"], "seen")
