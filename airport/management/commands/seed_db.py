from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from airport.models import (
    Airport,
    AirplaneType,
    Airplane,
    Crew,
    Route,
    Flight,
)

User = get_user_model()


class Command(BaseCommand):
    help = "Seed the database with sample data"

    def handle(self, *args, **options):
        self.stdout.write("Seeding database...")

        airports = [
            Airport.objects.get_or_create(
                name="Boryspil International Airport", closest_big_city="Kyiv"
            )[0],
            Airport.objects.get_or_create(
                name="Lviv Danylo Halytskyi Airport", closest_big_city="Lviv"
            )[0],
            Airport.objects.get_or_create(
                name="Heathrow Airport", closest_big_city="London"
            )[0],
            Airport.objects.get_or_create(
                name="Charles de Gaulle Airport", closest_big_city="Paris"
            )[0],
            Airport.objects.get_or_create(
                name="Frankfurt Airport", closest_big_city="Frankfurt"
            )[0],
            Airport.objects.get_or_create(
                name="Istanbul Airport", closest_big_city="Istanbul"
            )[0],
            Airport.objects.get_or_create(
                name="Warsaw Chopin Airport", closest_big_city="Warsaw"
            )[0],
            Airport.objects.get_or_create(
                name="JFK International Airport", closest_big_city="New York"
            )[0],
        ]
        self.stdout.write(f"  Created {len(airports)} airports")

        airplane_types = [
            AirplaneType.objects.get_or_create(name="Boeing 737")[0],
            AirplaneType.objects.get_or_create(name="Boeing 777")[0],
            AirplaneType.objects.get_or_create(name="Airbus A320")[0],
            AirplaneType.objects.get_or_create(name="Airbus A380")[0],
        ]
        self.stdout.write(f"  Created {len(airplane_types)} airplane types")

        airplanes = [
            Airplane.objects.get_or_create(
                name="SkyBird 1",
                defaults={
                    "rows": 30,
                    "seats_in_row": 6,
                    "airplane_type": airplane_types[0],
                },
            )[0],
            Airplane.objects.get_or_create(
                name="SkyBird 2",
                defaults={
                    "rows": 35,
                    "seats_in_row": 6,
                    "airplane_type": airplane_types[0],
                },
            )[0],
            Airplane.objects.get_or_create(
                name="Eagle 777",
                defaults={
                    "rows": 40,
                    "seats_in_row": 9,
                    "airplane_type": airplane_types[1],
                },
            )[0],
            Airplane.objects.get_or_create(
                name="AirCraft A320",
                defaults={
                    "rows": 28,
                    "seats_in_row": 6,
                    "airplane_type": airplane_types[2],
                },
            )[0],
            Airplane.objects.get_or_create(
                name="MegaJet A380",
                defaults={
                    "rows": 50,
                    "seats_in_row": 10,
                    "airplane_type": airplane_types[3],
                },
            )[0],
        ]
        self.stdout.write(f"  Created {len(airplanes)} airplanes")

        crew_members = [
            Crew.objects.get_or_create(first_name="John", last_name="Smith")[0],
            Crew.objects.get_or_create(first_name="Anna", last_name="Johnson")[0],
            Crew.objects.get_or_create(first_name="Oleksandr", last_name="Kovalenko")[
                0
            ],
            Crew.objects.get_or_create(first_name="Maria", last_name="Shevchenko")[0],
            Crew.objects.get_or_create(first_name="James", last_name="Williams")[0],
            Crew.objects.get_or_create(first_name="Sophie", last_name="Mueller")[0],
        ]
        self.stdout.write(f"  Created {len(crew_members)} crew members")

        routes = [
            Route.objects.get_or_create(
                source=airports[0], destination=airports[2], defaults={"distance": 2500}
            )[0],
            Route.objects.get_or_create(
                source=airports[0], destination=airports[3], defaults={"distance": 2300}
            )[0],
            Route.objects.get_or_create(
                source=airports[0], destination=airports[5], defaults={"distance": 1100}
            )[0],
            Route.objects.get_or_create(
                source=airports[1], destination=airports[6], defaults={"distance": 580}
            )[0],
            Route.objects.get_or_create(
                source=airports[2], destination=airports[7], defaults={"distance": 5500}
            )[0],
            Route.objects.get_or_create(
                source=airports[3], destination=airports[4], defaults={"distance": 480}
            )[0],
            Route.objects.get_or_create(
                source=airports[5], destination=airports[7], defaults={"distance": 8100}
            )[0],
        ]
        self.stdout.write(f"  Created {len(routes)} routes")

        now = timezone.now()
        flights = [
            Flight.objects.get_or_create(
                route=routes[0],
                airplane=airplanes[0],
                defaults={
                    "departure_time": now + timedelta(days=1, hours=8),
                    "arrival_time": now + timedelta(days=1, hours=12),
                },
            )[0],
            Flight.objects.get_or_create(
                route=routes[1],
                airplane=airplanes[3],
                defaults={
                    "departure_time": now + timedelta(days=2, hours=6),
                    "arrival_time": now + timedelta(days=2, hours=10),
                },
            )[0],
            Flight.objects.get_or_create(
                route=routes[2],
                airplane=airplanes[1],
                defaults={
                    "departure_time": now + timedelta(days=1, hours=14),
                    "arrival_time": now + timedelta(days=1, hours=17),
                },
            )[0],
            Flight.objects.get_or_create(
                route=routes[3],
                airplane=airplanes[3],
                defaults={
                    "departure_time": now + timedelta(days=3, hours=9),
                    "arrival_time": now + timedelta(days=3, hours=11),
                },
            )[0],
            Flight.objects.get_or_create(
                route=routes[4],
                airplane=airplanes[2],
                defaults={
                    "departure_time": now + timedelta(days=4, hours=10),
                    "arrival_time": now + timedelta(days=4, hours=19),
                },
            )[0],
            Flight.objects.get_or_create(
                route=routes[5],
                airplane=airplanes[4],
                defaults={
                    "departure_time": now + timedelta(days=2, hours=16),
                    "arrival_time": now + timedelta(days=2, hours=18),
                },
            )[0],
        ]
        for i, flight in enumerate(flights):
            flight.crew.add(
                crew_members[i % len(crew_members)],
                crew_members[(i + 1) % len(crew_members)],
            )
        self.stdout.write(f"  Created {len(flights)} flights")

        if not User.objects.filter(email="test@example.com").exists():
            User.objects.create_user(
                email="test@example.com",
                password="test12345",
            )

        if not User.objects.filter(email="admin@example.com").exists():
            User.objects.create_superuser(
                email="admin@example.com",
                password="admin12345",
            )

        self.stdout.write(self.style.SUCCESS("Database seeded successfully!"))
        self.stdout.write("  Users: test@example.com/test12345, admin@example.com/admin12345")
