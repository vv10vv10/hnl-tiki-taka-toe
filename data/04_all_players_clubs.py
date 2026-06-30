import json
import requests
import time

with open("data/jsons/players_clean.json", "r", encoding="utf-8") as f:
    players_load = json.load(f)

BASE_URL = "https://transfermarkt-api.fly.dev"

players = {}
i=1
mistakes = {}
for player_id, player_name in players_load.items():
    if(i%100==0):
        print("Players:",len(players))
        print("Mistakes:",len(mistakes))
        print()
    try:
        response = requests.get(f"{BASE_URL}/players/{player_id}/transfers")
        response.raise_for_status()
    except:
        #print("Greška",i)
        mistakes[player_id]=player_name
        i+=1
        continue

    data = response.json()
    clubs = set()
    for t in data["transfers"]:
        clubs.add(t["clubFrom"]["name"])
        clubs.add(t["clubTo"]["name"])

    try:
        response = requests.get(f"{BASE_URL}/players/{player_id}/profile")
        response.raise_for_status()
        #print("Igrač",i)
        i+=1
    except:
        #print("Greška",i)
        mistakes[player_id]=player_name
        i+=1
        continue

    data = response.json()
    citizenship=data["citizenship"]
    nameInHomeCountry=data.get("nameInHomeCountry") or player_name
    
    players[player_id] = {
        "name": player_name,
        "clubs": list(clubs),
        "citizenship": citizenship,
        "nameInHomeCountry": nameInHomeCountry
    }
    #time.sleep(1)


with open("data/jsons/players_data.json", "w", encoding="utf-8") as f:
    json.dump(players, f, ensure_ascii=False, indent=2)

with open("data/jsons/players_mistakes.json", "w", encoding="utf-8") as f:
    json.dump(mistakes, f, ensure_ascii=False, indent=2)