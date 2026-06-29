from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from rest_framework.test import APIClient

from airport.models import AirplaneType
from airport.serializers import AirplaneTypeSerializer

AIRPLANE_TYPE_URL = reverse("airport:airplane_type-list")


def detail_airplane_type_url(airplane_type_pk):
    return reverse("airport:airplane_type-detail", kwargs={"pk": airplane_type_pk})


def sample_airplane_type(**params):
    airplane_type = {
        "name": "Airplane_Type"
    }
    airplane_type.update(**params)
    return AirplaneType.objects.create(**airplane_type)


class UnauthorizedUser(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(AIRPLANE_TYPE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthorizedUser(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="user@user.com", password="1234"
        )

        self.client.force_authenticate(self.user)

    def test_airplane_type_list(self):
        airplane_type = sample_airplane_type()
        serializer = AirplaneTypeSerializer(airplane_type)

        res = self.client.get(AIRPLANE_TYPE_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(serializer.data, res.data["results"])

    def test_airplane_type_retrieve(self):
        airplane_type = sample_airplane_type()
        serializer_airplane_type = AirplaneTypeSerializer(airplane_type)

        res = self.client.get(detail_airplane_type_url(airplane_type.pk))

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer_airplane_type.data, res.data)

    def test_airplane_type_create_forbidden(self):
        payload = {
            "name": "Airplane_Type"
        }
        res = self.client.post(
            AIRPLANE_TYPE_URL, payload
        )

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminUser(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = get_user_model().objects.create_superuser(
            email="admin@admin.com", password="1234"
        )

        self.client.force_authenticate(self.user)

    def test_create_airplane_type_admin(self):
        payload = {
            "name": "Airplane_Type"
        }

        res = self.client.post(AIRPLANE_TYPE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_delete_airplane_type_admin(self):
        airplane_type = sample_airplane_type()

        res = self.client.delete(detail_airplane_type_url(airplane_type.pk))
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_update_airplane_type_admin(self):
        airplane_type = sample_airplane_type()
        payload = {
            "name": "Update_airplane_type"
        }
        url = detail_airplane_type_url(airplane_type.pk)

        res = self.client.put(url, payload)

        airplane_type.refresh_from_db()
        serializer_airplane_type = AirplaneTypeSerializer(airplane_type)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer_airplane_type.data, res.data)
