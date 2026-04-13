from rest_framework import status
from rest_framework.test import APITestCase

from apps.auth_identity.models import User
from apps.notifications.models import Notification
from apps.organizations.models import Organization, OrganizationMember
from apps.qr_engine.models import InteractionTemplate, QRCode, QROwnerMember
from apps.queue_control.models import Queue, QueueTicket


class TemplatePackApiTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            email="owner-phase7@example.com",
            phone_number="+15550070001",
            full_name="Owner Phase7",
            password="pass1234",
        )
        self.manager = User.objects.create_user(
            email="manager-phase7@example.com",
            phone_number="+15550070002",
            full_name="Manager Phase7",
            password="pass1234",
        )
        self.backup = User.objects.create_user(
            email="backup-phase7@example.com",
            phone_number="+15550070003",
            full_name="Backup Phase7",
            password="pass1234",
        )
        self.visitor = User.objects.create_user(
            email="visitor-phase7@example.com",
            phone_number="+15550070004",
            full_name="Visitor Phase7",
            password="pass1234",
        )
        self.organization = Organization.objects.create(
            name="Door Packs Org",
            slug="door-packs-org",
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
        self.queue = Queue.objects.create(
            organization=self.organization,
            name="Reception Queue",
            created_by_device_id="phase7-seed",
        )
        self.client.force_authenticate(self.owner)

    def test_pack_catalog_and_seed_create_first_reusable_template_packs(self):
        catalog_response = self.client.get("/api/v1/qr/template-packs/")
        self.assertEqual(catalog_response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            {pack["pack_key"] for pack in catalog_response.data["packs"]},
            {"queue_token", "doorbell_visitor_contact", "visitor_log"},
        )

        seed_response = self.client.post(
            "/api/v1/qr/template-packs/seed/",
            {"pack_keys": ["queue_token", "doorbell_visitor_contact", "visitor_log"]},
            format="json",
        )
        self.assertEqual(seed_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(seed_response.data["templates"]), 3)
        self.assertTrue(
            InteractionTemplate.objects.filter(schema_json__pack_key="queue_token").exists()
        )

    def test_queue_pack_admin_setup_scan_and_runtime_actions(self):
        self.client.post(
            "/api/v1/qr/template-packs/seed/",
            {"pack_keys": ["queue_token"]},
            format="json",
        )

        setup_response = self.client.post(
            "/api/v1/qr/template-packs/admin-setup/",
            {
                "pack_key": "queue_token",
                "organization": str(self.organization.id),
                "queue": str(self.queue.id),
                "name": "Reception QR",
                "owner_type": "organization",
                "owner_id": str(self.organization.id),
                "metadata_json": {"desk_label": "front"},
            },
            format="json",
        )
        self.assertEqual(setup_response.status_code, status.HTTP_201_CREATED)
        qr_code_id = setup_response.data["qr_code"]["id"]

        self.client.force_authenticate(self.visitor)
        scan_response = self.client.post(
            "/api/v1/qr/scan/",
            {
                "qr_code_id": qr_code_id,
                "device_id": "visitor-phone-1",
                "metadata": {"customer_name": "Amina"},
            },
            format="json",
        )
        self.assertEqual(scan_response.status_code, status.HTTP_201_CREATED)
        interaction_id = scan_response.data["interaction_id"]

        ticket = QueueTicket.objects.get(
            queue=self.queue,
            user=self.visitor,
        )
        self.assertEqual(ticket.number, 1)
        self.assertEqual(ticket.status, "issued")

        self.client.force_authenticate(self.owner)
        next_response = self.client.post(
            f"/api/v1/qr/codes/{qr_code_id}/runtime-action/",
            {"operation": "next"},
            format="json",
        )
        self.assertEqual(next_response.status_code, status.HTTP_200_OK)
        self.assertEqual(next_response.data["interaction"]["id"], interaction_id)
        self.assertEqual(next_response.data["ticket"]["status"], "called")

        complete_response = self.client.post(
            f"/api/v1/qr/interactions/{interaction_id}/actions/",
            {"action_key": "complete"},
            format="json",
        )
        self.assertEqual(complete_response.status_code, status.HTTP_200_OK)
        self.assertEqual(complete_response.data["status"], "completed")

        ticket.refresh_from_db()
        self.assertEqual(ticket.status, "completed")

    def test_doorbell_and_visitor_log_packs_capture_history_and_notifications(self):
        self.client.post(
            "/api/v1/qr/template-packs/seed/",
            {"pack_keys": ["doorbell_visitor_contact", "visitor_log"]},
            format="json",
        )

        doorbell_setup = self.client.post(
            "/api/v1/qr/template-packs/admin-setup/",
            {
                "pack_key": "doorbell_visitor_contact",
                "organization": str(self.organization.id),
                "name": "Front Door QR",
                "owner_type": "organization",
                "owner_id": str(self.organization.id),
            },
            format="json",
        )
        doorbell_qr_id = doorbell_setup.data["qr_code"]["id"]
        doorbell_qr = QRCode.objects.get(pk=doorbell_qr_id)
        QROwnerMember.objects.create(
            qr_code=doorbell_qr,
            owner=self.owner,
            member_user=self.backup,
            display_name="Backup Door",
            email=self.backup.email,
            phone=self.backup.phone_number,
            member_type="team",
            notify_role="bcc",
            priority=2,
            can_respond=True,
        )

        visitor_log_setup = self.client.post(
            "/api/v1/qr/template-packs/admin-setup/",
            {
                "pack_key": "visitor_log",
                "organization": str(self.organization.id),
                "name": "Visitor Log QR",
                "owner_type": "organization",
                "owner_id": str(self.organization.id),
            },
            format="json",
        )
        visitor_log_qr_id = visitor_log_setup.data["qr_code"]["id"]

        self.client.force_authenticate(self.visitor)
        doorbell_scan = self.client.post(
            "/api/v1/qr/scan/",
            {
                "qr_code_id": doorbell_qr_id,
                "metadata": {
                    "visitor_name": "Amina",
                    "message": "Package delivery",
                },
            },
            format="json",
        )
        self.assertEqual(doorbell_scan.status_code, status.HTTP_201_CREATED)
        interaction_detail = self.client.get(
            f"/api/v1/qr/interactions/{doorbell_scan.data['interaction_id']}/"
        )
        self.assertEqual(
            interaction_detail.data["payload_json"]["visitor_contact"]["visitor_name"],
            "Amina",
        )
        notified_users = set(
            Notification.objects.filter(
                source_entity_type="interaction_record",
                source_entity_id=doorbell_scan.data["interaction_id"],
            ).values_list("user__email", flat=True)
        )
        self.assertEqual(notified_users, {self.owner.email, self.manager.email, self.backup.email})

        visitor_log_scan = self.client.post(
            "/api/v1/qr/scan/",
            {
                "qr_code_id": visitor_log_qr_id,
                "metadata": {
                    "name": "Amina",
                    "purpose": "Registration desk",
                },
            },
            format="json",
        )
        self.assertEqual(visitor_log_scan.status_code, status.HTTP_201_CREATED)
        visitor_log_detail = self.client.get(
            f"/api/v1/qr/interactions/{visitor_log_scan.data['interaction_id']}/"
        )
        self.assertEqual(
            visitor_log_detail.data["payload_json"]["check_in_record"]["purpose"],
            "Registration desk",
        )
        audit_response = self.client.get(
            f"/api/v1/qr/interactions/{visitor_log_scan.data['interaction_id']}/audit-logs/"
        )
        self.assertEqual(len(audit_response.data), 1)
