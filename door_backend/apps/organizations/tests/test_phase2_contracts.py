from rest_framework import status
from rest_framework.test import APITestCase

from apps.auth_identity.models import User
from apps.organizations.models import Organization, OrganizationMember


class Phase2OrganizationContractsTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(phone="+15550010001", password="pass1234")
        self.child = User.objects.create_user(phone="+15550010002", password="pass1234")
        self.org = Organization.objects.create(
            name="Phase 2 Org",
            slug="phase-2-org",
            owner=self.user,
            created_by=self.user,
        )
        OrganizationMember.objects.create(
            organization=self.org,
            user=self.user,
            role="owner",
        )
        self.client.force_authenticate(self.user)

    def test_household_and_family_member_can_be_created(self):
        household_response = self.client.post(
            "/api/v1/organizations/households/",
            {
                "organization": str(self.org.id),
                "name": "Al Noor Family",
                "family_code": "NOOR-1",
            },
            format="json",
        )

        self.assertEqual(household_response.status_code, status.HTTP_201_CREATED)

        member_response = self.client.post(
            "/api/v1/organizations/household-members/",
            {
                "household": household_response.data["id"],
                "user": str(self.child.id),
                "relationship": "child",
                "hierarchy_level": 1,
            },
            format="json",
        )

        self.assertEqual(member_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(member_response.data["relationship"], "child")

    def test_attendance_session_and_record_can_be_created(self):
        session_response = self.client.post(
            "/api/v1/organizations/attendance-sessions/",
            {
                "organization": str(self.org.id),
                "title": "Bus Departure Roll Call",
                "session_type": "attendance",
                "attendance_mode": "qr",
                "status": "active",
            },
            format="json",
        )

        self.assertEqual(session_response.status_code, status.HTTP_201_CREATED)

        record_response = self.client.post(
            "/api/v1/organizations/attendance-records/",
            {
                "session": session_response.data["id"],
                "user": str(self.user.id),
                "status": "present",
                "check_in_method": "qr",
            },
            format="json",
        )

        self.assertEqual(record_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(record_response.data["status"], "present")

    def test_emergency_card_and_missing_person_case_can_be_created(self):
        emergency_response = self.client.post(
            "/api/v1/organizations/emergency-cards/",
            {
                "organization": str(self.org.id),
                "user": str(self.user.id),
                "blood_group": "O+",
                "emergency_contact_name": "Ahsan",
                "emergency_contact_phone": "+15551110000",
                "medical_notes": "Asthma inhaler required",
            },
            format="json",
        )

        self.assertEqual(emergency_response.status_code, status.HTTP_201_CREATED)

        missing_case_response = self.client.post(
            "/api/v1/organizations/missing-person-cases/",
            {
                "organization": str(self.org.id),
                "subject_user": str(self.child.id),
                "title": "Missing after prayer gathering",
                "status": "open",
                "last_seen_notes": "Last seen near gate 3",
                "priority": "high",
            },
            format="json",
        )

        self.assertEqual(missing_case_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(missing_case_response.data["status"], "open")
