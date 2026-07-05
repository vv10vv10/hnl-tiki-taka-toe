import requests
import json

BASE_URL = "https://transfermarkt-api.fly.dev"

seasons = range(2006, 2027)  # 2006–2026 uključivo
clubs_by_season = {}
all_clubs = {}

for season in seasons:
    url = f"{BASE_URL}/competitions/KR1/clubs"

    response = requests.get(url,params={"season_id": season})
    response.raise_for_status()
    data = response.json()
    clubs = []
    for c in data["clubs"]:
        clubs.append(c["id"])
    clubs_by_season[season] = clubs
    for club in data["clubs"]:
        all_clubs[club["id"]] = club["name"]

print(clubs_by_season)
print(all_clubs)

with open("data/jsons/clubs_by_season.json", "w", encoding="utf-8") as f:
    json.dump(clubs_by_season, f, ensure_ascii=False, indent=2)

with open("data/jsons/all_clubs.json", "w", encoding="utf-8") as f:
    json.dump(all_clubs, f, ensure_ascii=False, indent=2)