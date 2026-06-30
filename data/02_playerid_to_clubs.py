import requests

BASE_URL = "https://transfermarkt-api.fly.dev"

player_id = 27992

response = requests.get(f"{BASE_URL}/players/{player_id}/transfers")
response.raise_for_status()

data = response.json()

clubs = set()

for t in data["transfers"]:
    clubs.add(t["clubFrom"]["name"])
    clubs.add(t["clubTo"]["name"])

for c in clubs:
    print(c)