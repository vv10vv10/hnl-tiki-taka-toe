import json
from django.core.management.base import BaseCommand
from game.models import Country, Confederation


class Command(BaseCommand):
    help = "Seed countries"

    def handle(self, *args, **kwargs):

        with open("data/jsons/all_countries.json", "r", encoding="utf-8") as f:
            countries = json.load(f)

        created = 0

        for country_name, confederation_name in countries.items():
            confederation = Confederation.objects.get(name=confederation_name)

            country, created_flag = Country.objects.get_or_create(
                name=country_name,
                defaults={
                    "confederation": confederation
                }
            )

            if created_flag:
                created += 1

        self.stdout.write(
            self.style.SUCCESS(f"Done. Created {created} countries")
        )