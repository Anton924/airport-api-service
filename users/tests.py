from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


REGISTER_URL = reverse("user:register")
TOKEN_URL = reverse("user:token_obtain_pair")
TOKEN_REFRESH_URL = reverse("user:token_refresh")
ME_URL = reverse("user:user_info")


def sample_user(**params):
    payload = {
        "email": "user@user.com",
        "password": "test12345"
    }
    payload.update(**params)
    return get_user_model().objects.create_user(**payload)


class RegisterUserTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_register_user_success(self):
        payload = {
            "email": "newuser@example.com",
            "password": "test12345"
        }

        res = self.client.post(REGISTER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload["email"])
        self.assertTrue(user.check_password(payload["password"]))
        self.assertNotIn("password", res.data)

    def test_register_user_with_existing_email_fails(self):
        sample_user(email="duplicate@example.com")

        payload = {
            "email": "duplicate@example.com",
            "password": "test12345"
        }

        res = self.client.post(REGISTER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_user_with_short_password_fails(self):
        payload = {
            "email": "duplicate@example.com",
            "password": "123"
        }

        res = self.client.post(REGISTER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_user_is_not_staff_by_default(self):
        payload = {
            "email": "regular@example.com",
            "password": "test12345",
        }

        res = self.client.post(REGISTER_URL, payload)
        user = get_user_model().objects.get(email=payload["email"])
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertFalse(user.is_staff)


class TokenTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = sample_user(email="tokenuser@example.com")

    def test_obtain_token_for_valid_credentials(self):
        payload = {
            "email": "tokenuser@example.com",
            "password": "test12345",
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("access", res.data)
        self.assertIn("refresh", res.data)

    def test_obtain_token_with_wrong_password_fails(self):
        payload = {
            "email": "tokenuser@example.com",
            "password": "wrongpassword",
        }

        res = self.client.post(TOKEN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_token(self):
        payload = {
            "email": "tokenuser@example.com",
            "password": "test12345",
        }

        token_res = self.client.post(TOKEN_URL, payload)
        refresh_token = token_res.data["refresh"]

        res = self.client.post(TOKEN_REFRESH_URL, {"refresh": refresh_token})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("access", res.data)


class ManageUserUnauthorizedTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_retrieve_profile_unauthorized(self):
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class ManageUserAuthorizedTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = sample_user(
            email="profile@example.com"
        )

        self.client.force_authenticate(self.user)

    def test_retrieve_profile_success(self):
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["email"], self.user.email)
        self.assertNotIn("password", res.data)

    def test_update_profile(self):
        payload = {"email": "updated@example.com", "password": "newpass123"}

        res = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.email, payload["email"])
        self.assertTrue(self.user.check_password(payload["password"]))

    def test_cannot_set_is_staff_via_update(self):
        payload = {"is_staff": True}

        res = self.client.patch(ME_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertFalse(self.user.is_staff)
