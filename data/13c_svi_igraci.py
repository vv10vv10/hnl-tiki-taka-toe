import requests
from bs4 import BeautifulSoup
import time
import json

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

with open("data/jsons/clubs_by_season.json", "r", encoding="utf-8") as f:
    clubs_by_season = json.load(f)

players = {}

for season,club_list in clubs_by_season.items():
    for club_id in club_list:

        url = f"https://www.transfermarkt.com/a/kader/verein/{club_id}/saison_id/{season}"

        try:
            r = requests.get(url, headers=HEADERS, timeout=20)

            if r.status_code != 200:
                continue

            soup = BeautifulSoup(r.text, "html.parser")

            for a in soup.select("a[href*='/profil/spieler/']"):
                href = a.get("href")

                parts = href.split("/")

                if "spieler" not in parts:
                    continue

                try:
                    player_id = parts[parts.index("spieler") + 1]
                    if player_id == "8198#audio":
                        continue
                    name = a.get_text(strip=True)

                    players[player_id] = name

                except:
                    continue

            print(f"club {club_id} season {season} -> total {len(players)} players")

            time.sleep(1)

        except Exception as e:
            print("error:", id, season, e)

print("\nTOTAL UNIQUE PLAYERS:", len(players))

with open("data/jsons/all_players.json", "w", encoding="utf-8") as f:
    json.dump(players, f, ensure_ascii=False, indent=2)