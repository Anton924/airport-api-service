from django.contrib import admin

from airport.models import (
    Airport,
    Route,
    AirplaneType,
    Airplane,
    Crew,
    Flight,
    Order,
    Ticket,
)


@admin.register(Airport)
class AirportAdmin(admin.ModelAdmin):
    list_display = ("name", "closest_big_city")
    search_fields = ("name", "closest_big_city")
    ordering = ("name",)


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ("source", "destination", "distance")
    search_fields = ("source__name", "destination__name")
    list_filter = ("source", "destination")
    ordering = ("distance",)


@admin.register(AirplaneType)
class AirplaneTypeAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Airplane)
class AirplaneAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "rows",
        "seats_in_row",
        "airplane_type",
        "get_capacity"
    )
    search_fields = ("name",)
    list_filter = ("airplane_type",)
    ordering = ("name",)

    @admin.display(description="Capacity")
    def get_capacity(self, obj):
        return obj.capacity


@admin.register(Crew)
class CrewAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name")
    search_fields = ("first_name", "last_name")


@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = (
        "route",
        "airplane",
        "departure_time",
        "arrival_time",
        "get_crew"
    )
    search_fields = (
        "route__source__name",
        "route__destination__name",
        "airplane__name",
    )
    list_filter = ("airplane", "departure_time")
    ordering = ("departure_time",)

    @admin.display(description="Crew members")
    def get_crew(self, obj):
        return ", ".join(str(c) for c in obj.crew.all())


class TicketInline(admin.TabularInline):
    model = Ticket
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("user", "created_at", "get_tickets_count")
    search_fields = ("user__username", "user__email")
    list_filter = ("created_at",)
    ordering = ("-created_at",)
    inlines = [TicketInline]

    @admin.display(description="Tickets")
    def get_tickets_count(self, obj):
        return obj.tickets.count()


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ("row", "seat", "flight", "order")
    search_fields = (
        "flight__route__source__name",
        "flight__route__destination__name"
    )
    list_filter = ("flight",)
