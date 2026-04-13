from rest_framework import status
from rest_framework.test import APITestCase

from apps.auth_identity.models import User
from apps.organizations.models import Organization, OrganizationMember
from apps.queue_control.models import Queue


class QueueApiContractsTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(phone="+15550000003", password="pass1234")
        self.org = Organization.objects.create(
            name="Queue Org",
            slug="queue-org",
            owner=self.user,
            created_by=self.user,
        )
        OrganizationMember.objects.create(
            organization=self.org,
            user=self.user,
            role="owner",
        )
        self.queue = Queue.objects.create(
            organization=self.org,
            name="Reception",
            status="open",
        )
        self.client.force_authenticate(self.user)

    def test_join_queue_endpoint_issues_ticket_with_phase_one_payload(self):
        response = self.client.post(
            f"/api/v1/queues/{self.queue.id}/join/",
            {"device_id": "device-a"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("ticket_id", response.data)
        self.assertEqual(response.data["ticket_number"], 1)
        self.assertEqual(response.data["status"], "issued")
