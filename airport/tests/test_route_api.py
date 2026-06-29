from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from rest_framework.test import APIClient

from airport.models import Route, Airport
from airport.serializers import (
    RouteListSerializer,
    RouteDetailSerializer,
    RouteSerializer
)

ROUTE_URL = reverse("airport:route-list")


def detail_route_url(route_pk):
    return reverse("airport:route-detail", kwargs={"pk": route_pk})


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
        res = self.client.get(ROUTE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthorizedUser(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="user@user.com", password="1234"
        )

        self.client.force_authenticate(self.user)

    def test_route_list(self):
        route = sample_route()
        serializer = RouteListSerializer(route)

        res = self.client.get(ROUTE_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(serializer.data, res.data["results"])

    def test_route_retrieve(self):
        route = sample_route()
        serializer_route = RouteDetailSerializer(route)

        res = self.client.get(detail_route_url(route.pk))

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer_route.data, res.data)

    def test_route_create_forbidden(self):
        payload = {
            "source": Airport.objects.create(
                name="Airport_1", closest_big_city="Wroclaw"
            ),
            "destination": Airport.objects.create(
                name="Airport_2", closest_big_city="Warsaw"
            ),
            "distance": 296
        }
        res = self.client.post(
            ROUTE_URL, payload
        )

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminUser(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = get_user_model().objects.create_superuser(
            email="admin@admin.com", password="1234"
        )

        self.client.force_authenticate(self.user)

    def test_create_route_admin(self):
        airport_1 = Airport.objects.create(
            name="Airport_3", closest_big_city="Krakow"
        )
        airport_2 = Airport.objects.create(
            name="Airport_4", closest_big_city="Lodz"
        )
        payload = {
            "source": airport_1.pk,
            "destination": airport_2.pk,
            "distance": 296
        }

        res = self.client.post(ROUTE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_delete_route_admin(self):
        route = sample_route()

        res = self.client.delete(detail_route_url(route.pk))
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_update_route_admin(self):
        route = sample_route()
        airport_1 = Airport.objects.create(
            name="Airport_3", closest_big_city="Krakow"
        )
        airport_2 = Airport.objects.create(
            name="Airport_4", closest_big_city="Lodz"
        )
        payload = {
            "source": airport_1.pk,
            "destination": airport_2.pk,
            "distance": 100
        }
        url = detail_route_url(route.pk)

        res = self.client.put(url, payload)

        route.refresh_from_db()
        serializer_route = RouteSerializer(route)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer_route.data, res.data)

    def test_create_route_same_source_destination(self):
        airport = Airport.objects.create(
            name="Airport", closest_big_city="Wroclaw"
        )
        payload = {
            "source": airport.pk,
            "destination": airport.pk,
            "distance": 23
        }

        res = self.client.post(ROUTE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_route_negative_distance(self):
        airport_1 = Airport.objects.create(
            name="Airport_3", closest_big_city="Krakow"
        )
        airport_2 = Airport.objects.create(
            name="Airport_4", closest_big_city="Lodz"
        )
        payload = {
            "source": airport_1.pk,
            "destination": airport_2.pk,
            "distance": -1
        }

        res = self.client.post(ROUTE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
