import json
import requests

#with open("data/jsons/players_clean.json", "r", encoding="utf-8") as f:
#    players = json.load(f)
#print(len(players))
with open("data/jsons/players_data.json", "r", encoding="utf-8") as f:
    players = json.load(f)
#print(len(players))
players_mistakes={}
for id,value in players.items():
    if(len(value["clubs"])==0):
        players_mistakes[id]=value

with open("data/jsons/players_mistakes2.json", "w", encoding="utf-8") as f:
    json.dump(players_mistakes, f, ensure_ascii=False, indent=2)

#with open("data/jsons/players_mistakes.json", "r", encoding="utf-8") as f:
#    players_load = json.load(f)
#print(len(players_load))