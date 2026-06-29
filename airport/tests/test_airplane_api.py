import datetime
import os.path
import tempfile

from PIL import Image
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from rest_framework.test import APIClient

from airport.models import (
    AirplaneType,
    Airplane,
    Airport,
    Route,
    Flight
)
from airport.serializers import (
    AirplaneListSerializer,
    AirplaneDetailSerializer,
    AirplaneSerializer
)

AIRPLANE_URL = reverse("airport:airplane-list")
FLIGHT_URL = reverse("airport:flight-list")


def detail_airplane_url(airplane_pk):
    return reverse("airport:airplane-detail", kwargs={"pk": airplane_pk})


def detail_flight_url(flight_pk):
    return reverse("airport:flight-detail", kwargs={"pk": flight_pk})


def image_upload_url(airplane_pk):
    return reverse("airport:airplane-upload-image", kwargs={"pk": airplane_pk})


def sample_airplane(**params):
    airplane = {
        "name": "Airplane",
        "rows": 12,
        "seats_in_row": 6,
        "airplane_type": AirplaneType.objects.create(name="Airplane_Type"),
    }

    airplane.update(**params)
    return Airplane.objects.create(**airplane)


def sample_route(**params):
    route = {
        "source": Airport.objects.create(
            name="Airport_1", closest_big_city="Wroclaw"
        ),
        "destination": Airport.objects.create(
            name="Airport_2", closest_big_city="Warsaw"
        ),
        "distance": 296
    }
    route.update(**params)
    return Route.objects.create(**route)


class UnauthorizedUser(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(AIRPLANE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthorizedUser(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="user@user.com", password="1234"
        )

        self.client.force_authenticate(self.user)

    def test_airplane_list(self):
        airplane = sample_airplane()
        serializer = AirplaneListSerializer(airplane)

        res = self.client.get(AIRPLANE_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(serializer.data, res.data["results"])

    def test_airplane_retrieve(self):
        airplane = sample_airplane()
        serializer_airplane = AirplaneDetailSerializer(airplane)

        res = self.client.get(detail_airplane_url(airplane.pk))

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer_airplane.data, res.data)

    def test_airplane_create_forbidden(self):
        payload = {
            "name": "Airplane",
            "rows": 12,
            "seats_in_row": 6,
            "airplane_type": AirplaneType.objects.create(name="Airplane_Type"),
        }
        res = self.client.post(
            AIRPLANE_URL, payload
        )

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminUser(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = get_user_model().objects.create_superuser(
            email="admin@admin.com", password="1234"
        )

        self.client.force_authenticate(self.user)

    def test_create_airplane_admin(self):
        airplane_type = AirplaneType.objects.create(name="Airplane_Type")
        payload = {
            "name": "Airplane",
            "rows": 12,
            "seats_in_row": 6,
            "airplane_type": airplane_type.pk,
        }

        res = self.client.post(AIRPLANE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_delete_airplane_admin(self):
        airplane = sample_airplane()

        res = self.client.delete(detail_airplane_url(airplane.pk))
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_update_airplane_admin(self):
        airplane = sample_airplane()
        airplane_type = AirplaneType.objects.create(
            name="Airplane_Type_Update"
        )
        payload = {
            "name": "Airplane_update",
            "rows": 12,
            "seats_in_row": 6,
            "airplane_type": airplane_type.pk,
        }
        url = detail_airplane_url(airplane.pk)

        res = self.client.put(url, payload)

        airplane.refresh_from_db()
        serializer_airplane = AirplaneSerializer(airplane)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer_airplane.data, res.data)

    def test_create_airplane_invalid_rows(self):
        airplane_type = AirplaneType.objects.create(name="Airplane_Type")
        payload = {
            "name": "Airplane",
            "rows": 0,
            "seats_in_row": -1,
            "airplane_type": airplane_type.pk,
        }

        res = self.client.post(AIRPLANE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


class AirplaneImageUploadTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            email="admin@admin.com", password="1234"
        )
        self.client.force_authenticate(self.user)
        self.airplane = sample_airplane()

    def tearDown(self):
        self.airplane.image.delete()

    def test_upload_image_to_airplane(self):
        url = image_upload_url(self.airplane.pk)
        with tempfile.NamedTemporaryFile(suffix=".jpeg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(url, {"image": ntf}, format="multipart")

        self.airplane.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("image", res.data)
        self.assertTrue(os.path.exists(self.airplane.image.path))

    def test_upload_image_bad_request(self):
        url = image_upload_url(self.airplane.pk)
        res = self.client.post(url, {"image": "not image"}, format="multipart")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_image_to_airplane_list(self):
        url = AIRPLANE_URL
        airplane_type = AirplaneType.objects.create(name="Airplane_Type")
        with tempfile.NamedTemporaryFile(suffix=".jpeg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, "JPEG")
            ntf.seek(0)
            payload = {
                "name": "Airplane_Test_List_Image",
                "rows": 12,
                "seats_in_row": 6,
                "airplane_type": airplane_type.pk,
                "image": ntf
            }
            res = self.client.post(url, payload, format="multipart")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        airplane = Airplane.objects.get(name="Airplane_Test_List_Image")
        self.assertFalse(airplane.image)

    def test_image_url_is_shown_on_airplane_detail(self):
        url = image_upload_url(self.airplane.pk)
        with tempfile.NamedTemporaryFile(suffix=".jpeg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, "JPEG")
            ntf.seek(0)
            self.client.post(url, {"image": ntf}, format="multipart")

        res = self.client.get(AIRPLANE_URL)

        self.assertIn("image", res.data["results"][0].keys())

    def test_image_url_is_shown_on_flight_detail(self):
        flight = Flight.objects.create(
            route=sample_route(),
            airplane=self.airplane,
            departure_time=timezone.make_aware(
                datetime.datetime(2026, 6, 27, 14, 30)
            ),
            arrival_time=timezone.make_aware(
                datetime.datetime(2026, 6, 27, 16, 30)
            )
        )
        url = image_upload_url(self.airplane.pk)
        with tempfile.NamedTemporaryFile(suffix=".jpeg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, "JPEG")
            ntf.seek(0)
            self.client.post(url, {"image": ntf}, format="multipart")

        res = self.client.get(detail_flight_url(flight.pk))
        self.assertIn("image", res.data["airplane"].keys())
