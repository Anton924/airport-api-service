import pathlib
import uuid

from django.conf import settings
from django.db import models
from django.utils.text import slugify


class Airport(models.Model):
    name = models.CharField(max_length=255)
    closest_big_city = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Route(models.Model):
    source = models.ForeignKey("Airport", on_delete=models.CASCADE, related_name="source_routes")
    destination = models.ForeignKey("Airport", on_delete=models.CASCADE, related_name="destination_routes")
    distance = models.IntegerField()

    def __str__(self):
        return f"{self.source.name} - {self.destination.name}"


class AirplaneType(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


def airplane_image_path(instance: "Airplane", filename: str):
    filename = (f"{slugify(instance.name)}-{uuid.uuid4()}"
                + pathlib.Path(filename).suffix
                )
    return pathlib.Path("uploads/airplanes") / filename


class Airplane(models.Model):
    name = models.CharField(max_length=255)
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()
    airplane_type = models.ForeignKey(
        "AirplaneType",
        on_delete=models.PROTECT,
        related_name="airplanes"
    )
    image = models.ImageField(null=True, upload_to=airplane_image_path)

    @property
    def capacity(self):
        return self.rows * self.seats_in_row

    def __str__(self):
        return self.name


class Crew(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return self.full_name


class Flight(models.Model):
    route = models.ForeignKey("Route", on_delete=models.PROTECT, related_name="flights")
    airplane = models.ForeignKey("Airplane", on_delete=models.PROTECT, related_name="flights")
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    crew = models.ManyToManyField(to="Crew", related_name="flights")

    def __str__(self):
        return f"{self.route}, {self.departure_time}:{self.arrival_time}"


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders")

    def __str__(self):
        return f"{self.user}, {self.created_at}: {self.tickets.count()}"


class Ticket(models.Model):
    row = models.IntegerField()
    seat = models.IntegerField()
    flight = models.ForeignKey("Flight", on_delete=models.CASCADE, related_name="tickets")
    order = models.ForeignKey("Order", on_delete=models.CASCADE, related_name="tickets")


    class Meta:
        unique_together = ("row", "seat", "flight")

    def __str__(self):
        return f"Row: {self.row}, Seat: {self.seat}, {self.flight}"

