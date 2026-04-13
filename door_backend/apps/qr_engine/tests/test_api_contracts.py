from datetime import timedelta

from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.auth_identity.models import User
from apps.organizations.models import Organization, OrganizationMember
from apps.qr_engine.models import QRCode, QRScan, ScanToken


class QrApiContractsTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(phone="+15550000002", password="pass1234")
        self.org = Organization.objects.create(
            name="Door Org",
            slug="door-org",
            owner=self.user,
            created_by=self.user,
        )
        OrganizationMember.objects.create(
            organization=self.org,
            user=self.user,
            role="owner",
        )

    def test_redeeming_scan_token_uses_phase_one_status_lifecycle(self):
        qr_code = QRCode.objects.create(
            organization=self.org,
            label="Front Desk",
            entity_type="organization",
            mode="check_in",
            created_by=self.user,
        )
        scan = QRScan.objects.create(
            qr_code=qr_code,
            scanned_by=self.user,
            entity_type=qr_code.entity_type,
            mode=qr_code.mode,
        )
        token = ScanToken.objects.create(
            scan=scan,
            token="phase1-token",
            status="issued",
            expires_at=timezone.now() + timedelta(minutes=10),
        )

        self.client.force_authenticate(self.user)
        response = self.client.post(
            "/api/v1/qr/token/redeem/",
            {"token": token.token},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        token.refresh_from_db()
        self.assertEqual(token.status, "redeemed")
        self.assertIsNotNone(token.redeemed_at)
        self.assertEqual(str(token.redeemed_by_id), str(self.user.id))
