from rest_framework import status
from rest_framework.test import APITestCase

from apps.auth_identity.models import User


class Phase1IdentityApiTests(APITestCase):
    def test_register_requires_full_name_email_phone_number_and_password(self):
        response = self.client.post(
            "/api/v1/auth/register/",
            {
                "email": "",
                "phone_number": "",
                "full_name": "",
                "password": "",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data["errors"])
        self.assertIn("phone_number", response.data["errors"])
        self.assertIn("full_name", response.data["errors"])
        self.assertIn("password", response.data["errors"])

    def test_register_creates_account_with_unique_email_and_phone_number(self):
        response = self.client.post(
            "/api/v1/auth/register/",
            {
                "email": "owner@example.com",
                "phone_number": "+15550000011",
                "full_name": "Owner User",
                "password": "StrongPass123!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["ok"])
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertEqual(response.data["user"]["email"], "owner@example.com")
        self.assertEqual(response.data["user"]["phone_number"], "+15550000011")
        self.assertEqual(response.data["user"]["full_name"], "Owner User")

        user = User.objects.get(email="owner@example.com")
        self.assertEqual(user.phone_number, "+15550000011")
        self.assertFalse(user.is_email_verified)
        self.assertFalse(user.is_phone_verified)
        self.assertEqual(user.status, User.AccountStatus.ACTIVE)

    def test_register_rejects_duplicate_email(self):
        User.objects.create_user(
            email="owner@example.com",
            phone_number="+15550000011",
            full_name="Existing User",
            password="StrongPass123!",
        )

        response = self.client.post(
            "/api/v1/auth/register/",
            {
                "email": "owner@example.com",
                "phone_number": "+15550000012",
                "full_name": "New User",
                "password": "StrongPass123!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data["errors"])

    def test_register_rejects_duplicate_phone_number(self):
        User.objects.create_user(
            email="owner@example.com",
            phone_number="+15550000011",
            full_name="Existing User",
            password="StrongPass123!",
        )

        response = self.client.post(
            "/api/v1/auth/register/",
            {
                "email": "new@example.com",
                "phone_number": "+15550000011",
                "full_name": "New User",
                "password": "StrongPass123!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("phone_number", response.data["errors"])

    def test_login_accepts_email_and_password(self):
        User.objects.create_user(
            email="owner@example.com",
            phone_number="+15550000011",
            full_name="Existing User",
            password="StrongPass123!",
        )

        response = self.client.post(
            "/api/v1/auth/login/",
            {
                "identifier": "owner@example.com",
                "password": "StrongPass123!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["ok"])
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertEqual(response.data["user"]["email"], "owner@example.com")

    def test_login_accepts_phone_number_and_password(self):
        User.objects.create_user(
            email="owner@example.com",
            phone_number="+15550000011",
            full_name="Existing User",
            password="StrongPass123!",
        )

        response = self.client.post(
            "/api/v1/auth/login/",
            {
                "identifier": "+15550000011",
                "password": "StrongPass123!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["ok"])
        self.assertEqual(response.data["user"]["phone_number"], "+15550000011")
