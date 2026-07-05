import requests
import json
import os
import sys

with open("data/jsons/all_players_data.json", "r", encoding="utf-8") as f:
    players = json.load(f)

        

with open("data/jsons/all_players_data.json", "w", encoding="utf-8") as f:
    json.dump(players, f, ensure_ascii=False, indent=2)