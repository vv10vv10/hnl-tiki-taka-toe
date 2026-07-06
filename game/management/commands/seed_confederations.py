import json
from django.core.management.base import BaseCommand
from game.models import Confederation


class Command(BaseCommand):
    help = "Seed confederations"

    def handle(self, *args, **kwargs):

        with open("data/jsons/all_confederations.json", "r", encoding="utf-8") as f:
            confederations = json.load(f)

        created = 0

        for conf_name in confederations:
            obj, created_flag = Confederation.objects.get_or_create(
                name=conf_name
            )

            if created_flag:
                created += 1

        self.stdout.write(
            self.style.SUCCESS(f"Done. Created {created} confederations")
        )