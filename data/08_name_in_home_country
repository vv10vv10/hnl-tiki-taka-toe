import json
import requests
import time

with open("data/jsons/players_clean.json", "r", encoding="utf-8") as f:
    players_load = json.load(f)

BASE_URL = "https://transfermarkt-api.fly.dev"

response = requests.get(f"{BASE_URL}/players/205651/profile")
response.raise_for_status()

data = response.json()
print(data["nameInHomeCountry"])