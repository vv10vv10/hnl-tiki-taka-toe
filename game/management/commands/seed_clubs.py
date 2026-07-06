import json
from django.core.management.base import BaseCommand
from game.models import Club


class Command(BaseCommand):
    help = "Seed clubs"

    def handle(self, *args, **kwargs):

        with open("data/jsons/all_clubs.json", "r", encoding="utf-8") as f:
            clubs = json.load(f)

        created = 0

        for tm_id, name in clubs.items():

            club, created_flag = Club.objects.get_or_create(
                tm_id=tm_id,
                defaults={
                    "name": name
                }
            )

            if created_flag:
                created += 1

        self.stdout.write(
            self.style.SUCCESS(f"Done. Created {created} clubs")
        )