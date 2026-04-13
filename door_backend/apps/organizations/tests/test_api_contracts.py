from rest_framework import status
from rest_framework.test import APITestCase

from apps.auth_identity.models import User
from apps.organizations.models import OrganizationMember


class OrganizationApiContractsTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(phone="+15550000001", password="pass1234")
        self.client.force_authenticate(self.user)

    def test_creating_organization_creates_owner_membership_with_locked_role(self):
        response = self.client.post(
            "/api/v1/organizations/",
            {
                "name": "Door HQ",
                "slug": "door-hq",
                "type": "organization",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        membership = OrganizationMember.objects.get(
            organization_id=response.data["id"],
            user=self.user,
        )
        self.assertEqual(membership.role, "owner")
