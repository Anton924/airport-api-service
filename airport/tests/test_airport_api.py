from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from rest_framework.test import APIClient

from airport.models import Airport
from airport.serializers import AirportSerializer

AIRPORT_URL = reverse("airport:airport-list")


def detail_airport_url(airport_pk):
    return reverse("airport:airport-detail", kwargs={"pk": airport_pk})


def sample_airport(**params):
    airport = {
        "name": "Airport",
        "closest_big_city": "Wroclaw"
    }
    airport.update(**params)
    return Airport.objects.create(**airport)


class UnauthorizedUser(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(AIRPORT_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthorizedUser(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="user@user.com", password="1234"
        )

        self.client.force_authenticate(self.user)

    def test_airport_list(self):
        airport = sample_airport()
        serializer = AirportSerializer(airport)

        res = self.client.get(AIRPORT_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(serializer.data, res.data["results"])

    def test_airport_retrieve(self):
        airport = sample_airport()
        serializer_airport = AirportSerializer(airport)

        res = self.client.get(detail_airport_url(airport.pk))

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer_airport.data, res.data)

    def test_airport_create_forbidden(self):
        payload = {
            "name": "Airport",
            "closest_big_city": "Wroclaw"
        }
        res = self.client.post(
            AIRPORT_URL, payload
        )

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminUser(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = get_user_model().objects.create_superuser(
            email="admin@admin.com", password="1234"
        )

        self.client.force_authenticate(self.user)

    def test_create_airport_admin(self):
        payload = {
            "name": "Airport",
            "closest_big_city": "Wroclaw"
        }

        res = self.client.post(AIRPORT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_delete_airport_admin(self):
        airport = sample_airport()

        res = self.client.delete(detail_airport_url(airport.pk))
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_update_airport_admin(self):
        airport = sample_airport()
        payload = {
            "name": "Update_airport",
            "closest_big_city": "Warsaw"
        }
        url = detail_airport_url(airport.pk)

        res = self.client.put(url, payload)

        airport.refresh_from_db()
        serializer_airport = AirportSerializer(airport)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer_airport.data, res.data)
