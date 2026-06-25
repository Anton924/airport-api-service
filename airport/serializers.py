from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from airport.models import (
    Airport,
    AirplaneType,
    Airplane,
    Crew,
    Route,
    Flight,
    Ticket,
    Order,
)


class AirportSerializer(serializers.ModelSerializer):

    class Meta:
        model = Airport
        fields = ("id", "name", "closest_big_city")
        read_only_fields = ("id",)


class AirplaneTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = AirplaneType
        fields = ("id", "name")
        read_only_fields = ("id",)


class AirplaneSerializer(serializers.ModelSerializer):

    def validate(self, attrs):
        data = super(AirplaneSerializer, self).validate(attrs)
        Airplane.validate_airplane_seat_row(
            rows=attrs["rows"],
            seats_in_row=attrs["seats_in_row"],
            error_to_raise=ValidationError,
        )
        return data

    class Meta:
        model = Airplane
        fields = ("name", "rows", "seats_in_row", "airplane_type")


class AirplaneListSerializer(serializers.ModelSerializer):
    airplane_type = serializers.CharField(source="airplane_type.name")

    class Meta:
        model = Airplane
        fields = (
            "id",
            "name",
            "rows",
            "seats_in_row",
            "airplane_type",
            "capacity",
            "image",
        )


class AirplaneDetailSerializer(serializers.ModelSerializer):
    airplane_type = AirplaneTypeSerializer()

    class Meta:
        model = Airplane
        fields = (
            "id",
            "name",
            "rows",
            "seats_in_row",
            "airplane_type",
            "capacity",
            "image",
        )


class CrewSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name", "full_name")
        read_only_fields = ("id",)


class RouteSerializer(serializers.ModelSerializer):

    def validate(self, attrs):
        data = super(RouteSerializer, self).validate(attrs)
        Route.validate_route(
            source=attrs["source"],
            destination=attrs["destination"],
            distance=attrs["distance"],
        )
        return data

    class Meta:
        model = Route
        fields = ("source", "destination", "distance")


class RouteListSerializer(serializers.ModelSerializer):
    source = serializers.CharField(source="source.name")
    destination = serializers.CharField(source="destination.name")

    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")


class RouteDetailSerializer(serializers.ModelSerializer):
    source = AirportSerializer()
    destination = AirportSerializer()

    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")


class FlightSerializer(serializers.ModelSerializer):
    crew = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Crew.objects.all()
    )

    def validate(self, attrs):
        data = super(FlightSerializer, self).validate(attrs)
        Flight.validate_flight(
            departure_time=attrs["departure_time"],
            arrival_time=attrs["arrival_time"],
            error_to_raise=ValidationError,
        )
        return data

    class Meta:
        model = Flight
        fields = (
            "route",
            "airplane",
            "departure_time",
            "arrival_time",
            "crew"
        )


class FlightListSerializer(serializers.ModelSerializer):
    route = serializers.StringRelatedField()
    airplane = serializers.CharField(source="airplane.name")
    crew = serializers.StringRelatedField(many=True)
    tickets_available = serializers.IntegerField(read_only=True)

    class Meta:
        model = Flight
        fields = (
            "id",
            "route",
            "airplane",
            "departure_time",
            "arrival_time",
            "crew",
            "tickets_available",
        )


class TicketSeatsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ticket
        fields = ("row", "seat")


class FlightDetailSerializer(serializers.ModelSerializer):
    route = RouteDetailSerializer()
    airplane = AirplaneDetailSerializer()
    crew = CrewSerializer(many=True)
    tickets_available = serializers.IntegerField(read_only=True)
    taken_seats = TicketSeatsSerializer(many=True, source="tickets")

    class Meta:
        model = Flight
        fields = (
            "id",
            "route",
            "airplane",
            "departure_time",
            "arrival_time",
            "crew",
            "tickets_available",
            "taken_seats",
        )


class TicketSerializer(serializers.ModelSerializer):
    flight = serializers.StringRelatedField()

    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "flight")
        read_only_fields = ("id",)


class TicketCreateSerializer(serializers.ModelSerializer):
    flight = serializers.PrimaryKeyRelatedField(queryset=Flight.objects.all())

    class Meta:
        model = Ticket
        fields = ("row", "seat", "flight")

    def validate(self, attrs):
        data = super(TicketCreateSerializer, self).validate(attrs)
        Ticket.validate_seat(
            row=attrs["row"],
            seat=attrs["seat"],
            flight=attrs["flight"],
            error_to_raise=ValidationError,
        )
        return data


class OrderCreateSerializer(serializers.ModelSerializer):
    tickets = TicketCreateSerializer(many=True)

    def create(self, validated_data):
        with transaction.atomic():
            tickets = validated_data.pop("tickets")
            order = Order.objects.create(**validated_data)
            for ticket in tickets:
                Ticket.objects.create(order=order, **ticket)
            return order

    class Meta:
        model = Order
        fields = ("created_at", "tickets")
        read_only_fields = ("created_at",)


class OrderDetailSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True)
    user = serializers.StringRelatedField()

    class Meta:
        model = Order
        fields = ("id", "created_at", "tickets", "user")


class OrderListSerializer(serializers.ModelSerializer):
    tickets = serializers.StringRelatedField(many=True)

    class Meta:
        model = Order
        fields = ("id", "created_at", "tickets")


class AirplaneImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Airplane
        fields = (
            "id",
            "name",
            "image",
        )
        read_only_fields = ("id", "name")
