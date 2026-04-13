from rest_framework import status
from rest_framework.test import APITestCase

from apps.auth_identity.models import User
from apps.organizations.models import (
    Event,
    Group,
    GroupMember,
    Organization,
    OrganizationMember,
)


class OrganizationCleanupApiTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            email="owner@example.com",
            phone_number="+15550020001",
            full_name="Owner User",
            password="pass1234",
        )
        self.manager = User.objects.create_user(
            email="manager@example.com",
            phone_number="+15550020002",
            full_name="Manager User",
            password="pass1234",
        )
        self.group_leader = User.objects.create_user(
            email="leader@example.com",
            phone_number="+15550020003",
            full_name="Leader User",
            password="pass1234",
        )
        self.member = User.objects.create_user(
            email="member@example.com",
            phone_number="+15550020004",
            full_name="Member User",
            password="pass1234",
        )
        self.org = Organization.objects.create(
            name="Door Org",
            slug="door-org",
            owner=self.owner,
            created_by=self.owner,
        )
        OrganizationMember.objects.create(
            organization=self.org,
            user=self.owner,
            role="owner",
        )
        OrganizationMember.objects.create(
            organization=self.org,
            user=self.manager,
            role="manager",
        )
        OrganizationMember.objects.create(
            organization=self.org,
            user=self.group_leader,
            role="group_leader",
        )
        OrganizationMember.objects.create(
            organization=self.org,
            user=self.member,
            role="member",
        )

    def test_public_event_can_be_created_without_organization(self):
        self.client.force_authenticate(self.owner)

        response = self.client.post(
            "/api/v1/organizations/events/",
            {
                "name": "Global Launch",
                "scope": "public",
                "event_type": "custom",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNone(response.data["organization"])
        self.assertEqual(str(response.data["created_by"]), str(self.owner.id))

    def test_manager_can_create_group_with_future_flexible_team_type(self):
        self.client.force_authenticate(self.manager)

        response = self.client.post(
            "/api/v1/organizations/groups/",
            {
                "organization": str(self.org.id),
                "name": "Expo Ops Team",
                "group_type": "expo_team",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["group_type"], "expo_team")

    def test_member_cannot_create_group(self):
        self.client.force_authenticate(self.member)

        response = self.client.post(
            "/api/v1/organizations/groups/",
            {
                "organization": str(self.org.id),
                "name": "Office Team",
                "group_type": "office_team",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_group_leader_can_add_group_member_with_member_role(self):
        group = Group.objects.create(
            organization=self.org,
            name="Family A",
            group_type="family",
            leader=self.group_leader,
        )
        GroupMember.objects.create(
            group=group,
            user=self.group_leader,
            role="group_leader",
            added_by=self.owner,
        )
        self.client.force_authenticate(self.group_leader)

        response = self.client.post(
            "/api/v1/organizations/group-members/",
            {
                "group": str(group.id),
                "user": str(self.member.id),
                "role": "member",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["role"], "member")

    def test_owner_can_list_groups_for_organization(self):
        Group.objects.create(
            organization=self.org,
            name="Clinic Team",
            group_type="clinic_team",
            leader=self.owner,
        )
        self.client.force_authenticate(self.owner)

        response = self.client.get(f"/api/v1/organizations/groups/?organization={self.org.id}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_existing_organization_member_role_is_normalized_to_member(self):
        self.assertEqual(
            OrganizationMember.objects.get(organization=self.org, user=self.member).role,
            "member",
        )
