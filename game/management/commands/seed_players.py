import json
from django.core.management.base import BaseCommand
from game.models import Player, Club, Country


class Command(BaseCommand):
    help = "Seed players"

    def handle(self, *args, **kwargs):

        created = 0

        with open("data/jsons/all_players_data.json", "r", encoding="utf-8") as f:
            players = json.load(f)

        for tm_id, value in players.items():

            name = value.get("name")
            clubs = value.get("klubovi", [])
            countries = value.get("citizenship", [])

            if not name:
                continue

            player, created_flag = Player.objects.get_or_create(
                tm_id=tm_id,
                defaults={
                    "name": name,
                    "name_in_home_country": value.get("nameInHomeCountry") or "",
                    "is_retired": value.get("isRetired") or False,
                    "market_value": value.get("marketValue") or 0,
                    "player_slug": value.get("player_slug") or "",

                    "hnl_nastupi": value.get("hnl_nastupi") or 0,
                    "kup_nastupi": value.get("kup_nastupi") or 0,
                    "superkup_nastupi": value.get("superkup_nastupi") or 0,
                    "a_repka_nastupi": value.get("A_repka_nastupi") or 0,

                    "hnl_golovi": value.get("hnl_golovi") or 0,
                    "finale_kupa_nastupi": value.get("finale_kupa_nastupi") or 0,
                    "finale_kupa_golovi": value.get("finale_kupa_golovi") or 0,
                    "superkup_golovi": value.get("superkup_golovi") or 0,

                    "najbolji_strijelac": value.get("najbolji_strijelac") or 0,

                    "hnl_naslovi": value.get("hnl_naslovi") or 0,
                    "kup_naslovi": value.get("kup_naslovi") or 0,
                    "superkup_naslovi": value.get("superkup_naslovi") or 0,
                }
            )

            # CLUBS
            for club_id in clubs:
                club = Club.objects.filter(tm_id=club_id).first()
                if club:
                    player.clubs.add(club)

            # COUNTRIES
            for country_name in countries:
                country = Country.objects.filter(name=country_name).first()
                if country:
                    player.countries.add(country)

            if created_flag:
                created += 1

        self.stdout.write(
            self.style.SUCCESS(f"Done. Created {created} players")
        )