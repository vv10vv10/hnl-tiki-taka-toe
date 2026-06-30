import requests

BASE_URL = "https://transfermarkt-api.fly.dev"

player_name = "Luka Modric"

response = requests.get(f"{BASE_URL}/players/search/{player_name}")
response.raise_for_status()

data = response.json()

players = data["results"]

for player in players:
    print(player)