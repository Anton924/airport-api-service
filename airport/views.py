import datetime


from django.db.models import F
from django.db.models.aggregates import Count
from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiExample
)
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from airport.models import (
    Airport,
    AirplaneType,
    Airplane,
    Crew,
    Route,
    Flight,
    Order
)
from airport.serializers import (
    AirportSerializer,
    AirplaneTypeSerializer,
    AirplaneListSerializer,
    AirplaneDetailSerializer,
    AirplaneSerializer,
    CrewSerializer,
    RouteDetailSerializer,
    RouteListSerializer,
    RouteSerializer,
    FlightListSerializer,
    FlightSerializer,
    FlightDetailSerializer,
    OrderListSerializer,
    OrderCreateSerializer,
    OrderDetailSerializer,
    AirplaneImageSerializer,
)


class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer


class AirplaneTypeViewSet(viewsets.ModelViewSet):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer


class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.select_related("airplane_type")

    def get_serializer_class(self):
        if self.action == "list":
            return AirplaneListSerializer
        elif self.action == "retrieve":
            return AirplaneDetailSerializer
        elif self.action == "upload_image":
            return AirplaneImageSerializer
        return AirplaneSerializer

    @extend_schema(description="Upload an image for a specific airplane")
    @action(
        methods=["POST"],
        detail=True,
        permission_classes=[IsAdminUser],
        url_path="upload-image",
    )
    def upload_image(self, request, pk=None):
        airplane = self.get_object()
        serializer = AirplaneImageSerializer(airplane, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(
            data=serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.select_related("source", "destination")

    def get_serializer_class(self):
        if self.action == "list":
            return RouteListSerializer
        elif self.action == "retrieve":
            return RouteDetailSerializer
        return RouteSerializer


def params_to_int(params: str) -> list[int]:
    return [int(param) for param in params.split(",")]


class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return FlightListSerializer
        elif self.action == "retrieve":
            return FlightDetailSerializer
        return FlightSerializer

    def get_queryset(self):
        queryset = (
            Flight.objects.select_related(
                "route__source",
                "route__destination",
                "airplane__airplane_type"
            )
            .prefetch_related("crew")
            .annotate(
                tickets_available=(
                        F("airplane__rows") * F("airplane__seats_in_row")
                    )
                - Count("tickets")
            )
        )
        route = self.request.query_params.get("route")
        departure_date = self.request.query_params.get("departure_date")
        source_city = self.request.query_params.get("source_city")
        destination_city = self.request.query_params.get("destination_city")

        if route:
            queryset = queryset.filter(route__in=params_to_int(route))
        if departure_date:
            departure_date = datetime.datetime.strptime(
                departure_date, "%d/%m/%y"
            )
            queryset = queryset.filter(departure_time__date=departure_date)
        if source_city:
            queryset = queryset.filter(
                route__source__closest_big_city=source_city
            )
        if destination_city:
            queryset = queryset.filter(
                route__destination__closest_big_city=destination_city
            )

        return queryset

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="route",
                type={"type": "list", "items": {"type": "number"}},
                description="Filter flights by route ids (comma-separated)",
                required=False,
                examples=[
                    OpenApiExample(
                        name="Single route",
                        value="1",
                    ),
                    OpenApiExample(
                        name="Multiple routes",
                        value="1,2,3",
                    ),
                ],
            ),
            OpenApiParameter(
                name="departure_date",
                type=str,
                description="Filter flights by departure date",
                required=False,
                examples=[
                    OpenApiExample(
                        name="Example date",
                        value="25/06/26",
                    ),
                ],
            ),
            OpenApiParameter(
                name="source_city",
                type=str,
                description="Filter flights by departure city name",
                required=False,
                examples=[
                    OpenApiExample(
                        name="Kyiv",
                        value="Kyiv",
                    ),
                    OpenApiExample(
                        name="London",
                        value="London",
                    ),
                ],
            ),
            OpenApiParameter(
                name="destination_city",
                type=str,
                description="Filter flights by arrival city name",
                required=False,
                examples=[
                    OpenApiExample(
                        name="Paris",
                        value="Paris",
                    ),
                    OpenApiExample(
                        name="Istanbul",
                        value="Istanbul",
                    ),
                ],
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class OrderViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Order.objects.all()
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer
        elif self.action == "create":
            return OrderCreateSerializer
        return OrderDetailSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related(
            "tickets__flight"
        )

    def perform_create(self, serializer):
        return serializer.save(user=self.request.user)
