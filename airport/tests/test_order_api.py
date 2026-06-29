import datetime

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
    Flight,
    Order,
    Ticket
)
from airport.serializers import (
    OrderListSerializer,
    OrderDetailSerializer
)

ORDER_URL = reverse("airport:order-list")


def detail_order_url(order_pk):
    return reverse("airport:order-detail", kwargs={"pk": order_pk})


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


def sample_order(user, **params):
    flight = sample_flight()
    order = {
        "user": user,
        "tickets":
            [
                {
                    "row": 1,
                    "seat": 1,
                    "flight": flight
                },
                {
                    "row": 1,
                    "seat": 2,
                    "flight": flight
                },
                {
                    "row": 1,
                    "seat": 3,
                    "flight": flight
                }
            ]
    }
    order.update(**params)
    order_instance = Order.objects.create(user=order.get("user"))
    for ticket in order.get("tickets"):
        Ticket.objects.create(**ticket, order=order_instance)
    return order_instance


class UnauthorizedUser(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(ORDER_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthorizedUser(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="user@user.com", password="1234"
        )

        self.client.force_authenticate(self.user)

    def test_order_list(self):
        order = sample_order(user=self.user)
        serializer = OrderListSerializer(order)

        res = self.client.get(ORDER_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(serializer.data, res.data["results"])

    def test_order_retrieve(self):
        order = sample_order(user=self.user)
        serializer_order = OrderDetailSerializer(order)

        res = self.client.get(detail_order_url(order.pk))

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer_order.data, res.data)

    def test_create_order(self):
        flight = sample_flight()
        payload = {
            "tickets":
                [
                    {
                        "row": 1,
                        "seat": 1,
                        "flight": flight.pk
                    },
                    {
                        "row": 1,
                        "seat": 2,
                        "flight": flight.pk
                    },
                    {
                        "row": 1,
                        "seat": 3,
                        "flight": flight.pk
                    }
                ]
        }
        res = self.client.post(
            ORDER_URL, payload, format="json"
        )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_delete_order(self):
        order = sample_order(user=self.user)
        url = detail_order_url(order_pk=order.pk)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_create_order_invalid_seat(self):
        flight = sample_flight()
        payload = {
            "tickets":
                [
                    {
                        "row": 1,
                        "seat": 0,
                        "flight": flight.pk
                    },
                ]
        }
        res = self.client.post(ORDER_URL, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_order_airplane_out_of_space(self):
        flight = sample_flight(
            airplane=sample_airplane(rows=2, seats_in_row=1)
        )
        payload = {
            "tickets":
                [
                    {
                        "row": 1,
                        "seat": 1,
                        "flight": flight.pk
                    },
                    {
                        "row": 2,
                        "seat": 1,
                        "flight": flight.pk
                    },
                    {
                        "row": 3,
                        "seat": 1,
                        "flight": flight.pk
                    }
                ]
        }
        res = self.client.post(ORDER_URL, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
