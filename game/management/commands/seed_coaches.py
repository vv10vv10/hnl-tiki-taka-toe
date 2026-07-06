import json
from django.core.management.base import BaseCommand
from game.models import Coach


class Command(BaseCommand):
    help = "Seed coaches"

    def handle(self, *args, **kwargs):

        with open("data/jsons/all_coaches.json", "r", encoding="utf-8") as f:
            coaches = json.load(f)

        created = 0

        for tm_id, name in coaches.items():

            coach, created_flag = Coach.objects.get_or_create(
                tm_id=tm_id,
                defaults={
                    "name": name
                }
            )

            if created_flag:
                created += 1

        self.stdout.write(
            self.style.SUCCESS(f"Done. Created {created} coaches")
        )