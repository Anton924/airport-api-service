from django.urls import path, include
from rest_framework import routers

from airport.views import (
    AirportViewSet,
    AirplaneTypeViewSet,
    AirplaneViewSet,
    CrewViewSet,
    RouteViewSet,
    FlightViewSet,
    OrderViewSet,
)

router = routers.DefaultRouter()

router.register("airports", AirportViewSet, basename="airport")

router.register(
    "airplane-types",
    AirplaneTypeViewSet,
    basename="airplane_type"
)

router.register("airplanes", AirplaneViewSet, basename="airplane")

router.register("crew", CrewViewSet, basename="crew")

router.register("routes", RouteViewSet, basename="route")

router.register("flights", FlightViewSet, basename="flight")

router.register("orders", OrderViewSet, basename="order")


urlpatterns = [path("", include(router.urls))]

app_name = "airport"
