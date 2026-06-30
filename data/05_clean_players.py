import json

with open("data/jsons/players.json", "r", encoding="utf-8") as f:
    players = json.load(f)

players2 = {}
for id,value in players.items():
    if(players[id] == ""):
        continue
    players2[id] = value

with open("data/jsons/players_clean.json", "w", encoding="utf-8") as f:
    json.dump(players2, f, ensure_ascii=False, indent=2)