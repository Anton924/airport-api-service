import pathlib
import uuid
import datetime

from django.conf import settings
from django.db import models
from django.db.models import UniqueConstraint
from django.utils.text import slugify
from rest_framework.exceptions import ValidationError


class Airport(models.Model):
    name = models.CharField(max_length=255)
    closest_big_city = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Route(models.Model):
    source = models.ForeignKey(
        "Airport", on_delete=models.CASCADE, related_name="source_routes"
    )
    destination = models.ForeignKey(
        "Airport", on_delete=models.CASCADE, related_name="destination_routes"
    )
    distance = models.IntegerField()

    def __str__(self):
        return f"{self.source.name} - {self.destination.name}"

    @staticmethod
    def validate_route(
        source: Airport,
        destination: Airport,
        distance: int,
        error_to_raise=ValidationError,
    ):
        if source == destination:
            raise error_to_raise(
                "Source and destination airports "
                "cannot be the same"
            )
        if distance <= 0:
            raise error_to_raise("Distance must be greater than 0")

    def clean(self):
        Route.validate_route(
            source=self.source,
            destination=self.destination,
            distance=self.distance,
            error_to_raise=ValidationError,
        )


class AirplaneType(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


def airplane_image_path(instance: "Airplane", filename: str):
    filename = (
        f"{slugify(instance.name)}-"
        f"{uuid.uuid4()}" +
        pathlib.Path(filename).suffix
    )
    return pathlib.Path("uploads/airplanes") / filename


class Airplane(models.Model):
    name = models.CharField(max_length=255)
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()
    airplane_type = models.ForeignKey(
        "AirplaneType", on_delete=models.PROTECT, related_name="airplanes"
    )
    image = models.ImageField(
        null=True,
        blank=True,
        upload_to=airplane_image_path
    )

    @property
    def capacity(self):
        return self.rows * self.seats_in_row

    def __str__(self):
        return self.name

    @staticmethod
    def validate_airplane_seat_row(
        rows: int, seats_in_row: int, error_to_raise=ValidationError
    ):
        if rows <= 0 or seats_in_row <= 0:
            raise error_to_raise("Row and seat must be >= 1")

    def clean(self):
        Airplane.validate_airplane_seat_row(
            rows=self.rows,
            seats_in_row=self.seats_in_row,
            error_to_raise=ValidationError,
        )


class Crew(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return self.full_name

    class Meta:
        verbose_name_plural = "crew"


class Flight(models.Model):
    route = models.ForeignKey(
        "Route",
        on_delete=models.PROTECT,
        related_name="flights"
    )
    airplane = models.ForeignKey(
        "Airplane", on_delete=models.PROTECT, related_name="flights"
    )
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    crew = models.ManyToManyField(to="Crew", related_name="flights")

    def __str__(self):
        return f"{self.route}, {self.departure_time}:{self.arrival_time}"

    @staticmethod
    def validate_flight(
        departure_time: datetime.datetime,
        arrival_time: datetime.datetime,
        error_to_raise=ValidationError,
    ):
        if departure_time >= arrival_time:
            raise error_to_raise("Arrival time must be after departure time")

    def clean(self):
        Flight.validate_flight(
            departure_time=self.departure_time,
            arrival_time=self.arrival_time,
            error_to_raise=ValidationError,
        )


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders"
    )

    def __str__(self):
        return f"{self.user}, {self.created_at}: {self.tickets.count()}"


class Ticket(models.Model):
    row = models.IntegerField()
    seat = models.IntegerField()
    flight = models.ForeignKey(
        "Flight", on_delete=models.CASCADE, related_name="tickets"
    )
    order = models.ForeignKey(
        "Order",
        on_delete=models.CASCADE,
        related_name="tickets"
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["row", "seat", "flight"], name="unique_seat_for_flight"
            )
        ]

    def __str__(self):
        return f"Row: {self.row}, Seat: {self.seat}, {self.flight}"

    @staticmethod
    def validate_seat(
        row: int, seat: int, flight: Flight, error_to_raise=ValidationError
    ):
        if flight.tickets.count() + 1 > flight.airplane.capacity:
            raise error_to_raise(
                detail=f"For flight:{flight} you can buy "
                       f"{flight.airplane.capacity - flight.tickets.count()}"
                       f" tickets"
            )

        if not (
            0 < row <= flight.airplane.rows and
            0 < seat <= flight.airplane.seats_in_row
        ):
            raise error_to_raise(
                detail=f"Seat has to be in range: 1 to "
                       f"{flight.airplane.seats_in_row}, "
                f"Row has to be in range: 1 to {flight.airplane.rows}"
            )

    def clean(self):
        Ticket.validate_seat(
            row=self.row,
            seat=self.seat,
            flight=self.flight,
            error_to_raise=ValidationError,
        )
