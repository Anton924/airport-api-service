import datetime

from django.contrib.auth import get_user_model
from django.db.models import F, Count
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from rest_framework.test import APIClient

from airport.models import (
    Airport,
    AirplaneType,
    Airplane,
    Route,
    Flight
)
from airport.serializers import (
    FlightSerializer,
    FlightListSerializer,
    FlightDetailSerializer
)

FLIGHT_URL = reverse("airport:flight-list")


def detail_flight_url(flight_pk):
    return reverse("airport:flight-detail", kwargs={"pk": flight_pk})


def sample_airplane(**params):
    airplane_type = {
        "name": "Airplane",
        "rows": 12,
        "seats_in_row": 6,
        "airplane_type": AirplaneType.objects.create(name="Airplane_Type"),
    }

    airplane_type.update(**params)
    return Airplane.objects.create(**airplane_type)


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


def sample_flight(**params):
    flight = {
        "route": sample_route(),
        "airplane": sample_airplane(),
        "departure_time": timezone.make_aware(
            datetime.datetime(2026, 6, 27, 14, 30)
        ),
        "arrival_time": timezone.make_aware(
            datetime.datetime(2026, 6, 27, 16, 30)
        )
    }
    flight.update(**params)
    return Flight.objects.create(**flight)


class UnauthorizedUser(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(FLIGHT_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthorizedUser(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="user@user.com", password="1234"
        )

        self.client.force_authenticate(self.user)

    def test_flight_list(self):
        flight = sample_flight()
        flight = Flight.objects.annotate(
            tickets_available=(
                    F("airplane__rows") *
                    F("airplane__seats_in_row") -
                    Count("tickets")
            )
        ).get(pk=flight.pk)
        serializer = FlightListSerializer(flight)

        res = self.client.get(FLIGHT_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(serializer.data, res.data["results"])

    def test_flight_retrieve_with_taken_seats(self):
        flight = sample_flight()
        flight = Flight.objects.annotate(
            tickets_available=(
                    F("airplane__rows") *
                    F("airplane__seats_in_row") -
                    Count("tickets")
            )

        ).get(pk=flight.pk)
        serializer_flight = FlightDetailSerializer(flight)

        res = self.client.get(detail_flight_url(flight.pk))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer_flight.data, res.data)

    def test_flight_create_forbidden(self):
        payload = {
            "route": sample_route(),
            "airplane": sample_airplane(),
            "departure_time": timezone.make_aware(
                datetime.datetime(2026, 6, 27, 14, 30)
            ),
            "arrival_time": timezone.make_aware(
                datetime.datetime(2026, 6, 27, 16, 30)
            )
        }
        res = self.client.post(
            FLIGHT_URL, payload
        )

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_filter_by_source_city_and_destiny_city(self):
        airport_1 = Airport.objects.create(
            name="Airport_1",
            closest_big_city="Wroclaw"
        )
        airport_2 = Airport.objects.create(
            name="Airport_2",
            closest_big_city="Krakow"
        )
        route_1 = sample_route(source=airport_1, destination=airport_2)
        route_2 = sample_route(source=airport_2, destination=airport_1)
        flight_1 = sample_flight(route=route_1)
        flight_2 = sample_flight(route=route_2)
        flight_1 = Flight.objects.annotate(
            tickets_available=(
                    F("airplane__rows") *
                    F("airplane__seats_in_row") -
                    Count("tickets")
            )

        ).get(pk=flight_1.pk)
        flight_2 = Flight.objects.annotate(
            tickets_available=(
                    F("airplane__rows") *
                    F("airplane__seats_in_row") -
                    Count("tickets")
            )

        ).get(pk=flight_2.pk)
        flight_1 = FlightListSerializer(flight_1)
        flight_2 = FlightListSerializer(flight_2)

        res = self.client.get(FLIGHT_URL, data={"source_city": "Wroclaw"})
        self.assertIn(flight_1.data, res.data["results"])
        self.assertNotIn(flight_2.data, res.data["results"])
        res = self.client.get(FLIGHT_URL, data={"destination_city": "Krakow"})
        self.assertIn(flight_1.data, res.data["results"])
        self.assertNotIn(flight_2.data, res.data["results"])

    def test_filter_by_departure_date(self):
        flight_1 = sample_flight(departure_time=timezone.make_aware(
            datetime.datetime(2026, 6, 27, 14, 30))
        )
        flight_2 = sample_flight(departure_time=timezone.make_aware(
            datetime.datetime(2026, 6, 28, 14, 30))
        )

        res = self.client.get(FLIGHT_URL, data={"departure_date": "27/06/26"})
        self.assertEqual(len(res.data["results"]), 1)
        self.assertEqual(res.data["results"][0].get("id"), flight_1.pk)
        self.assertNotEqual(res.data["results"][0].get("id"), flight_2.pk)

    def test_filter_by_route(self):
        airport_1 = Airport.objects.create(
            name="Airport_1",
            closest_big_city="Wroclaw"
        )
        airport_2 = Airport.objects.create(
            name="Airport_2",
            closest_big_city="Krakow"
        )
        route_1 = sample_route(source=airport_1, destination=airport_2)
        route_2 = sample_route(source=airport_2, destination=airport_1)
        flight_1 = sample_flight(route=route_1)
        flight_2 = sample_flight(route=route_2)

        res = self.client.get(FLIGHT_URL, data={"route": f"{route_1.pk}"})
        self.assertEqual(len(res.data["results"]), 1)
        self.assertEqual(res.data["results"][0].get("id"), flight_1.pk)
        self.assertNotEqual(res.data["results"][0].get("id"), flight_2.pk)


class AdminUser(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = get_user_model().objects.create_superuser(
            email="admin@admin.com", password="1234"
        )

        self.client.force_authenticate(self.user)

    def test_create_flight_admin(self):
        payload = {
            "route": sample_route().pk,
            "airplane": sample_airplane().pk,
            "departure_time": timezone.make_aware(
                datetime.datetime(2026, 6, 27, 14, 30)
            ),
            "arrival_time": timezone.make_aware(
                datetime.datetime(2026, 6, 27, 16, 30)
            )
        }

        res = self.client.post(FLIGHT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_delete_flight_admin(self):
        flight = sample_flight()

        res = self.client.delete(detail_flight_url(flight.pk))
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_update_flight_admin(self):
        flight = sample_flight()
        payload = {
            "route": sample_route().pk,
            "airplane": sample_airplane().pk,
            "departure_time": timezone.make_aware(
                datetime.datetime(2026, 6, 27, 15, 30)
            ),
            "arrival_time": timezone.make_aware(
                datetime.datetime(2026, 6, 27, 17, 30)
            )
        }
        url = detail_flight_url(flight.pk)

        res = self.client.put(url, payload)

        flight.refresh_from_db()
        serializer_flight = FlightSerializer(flight)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer_flight.data, res.data)
