import requests
import json
import os



with open("data/jsons/all_players_data.json", "r", encoding="utf-8") as f:
    players = json.load(f)

with open("data/jsons/mistakes_players_data.json", "r", encoding="utf-8") as f:
    mistakes = json.load(f)
# osobni podaci
BASE_URL = "https://transfermarkt-api.fly.dev"

i=1
j=1

for tm_id in list(mistakes.keys()):
    print(tm_id,i)
    i+=1
    failed = False
    try:
        response = requests.get(f"{BASE_URL}/players/{tm_id}/profile",timeout=10)
        data = response.json()
        name=data["name"]
        citizenship=data["citizenship"]
        nameInHomeCountry=data.get("nameInHomeCountry") or name
        isRetired=data["isRetired"]
        marketValue=data.get("marketValue") or 0
        player_slug=data["url"].split("/")[3]
        #rijesit dateOfBirth
    except Exception as e:
        name=None
        citizenship=None
        nameInHomeCountry=None
        isRetired=None
        marketValue=None
        player_slug=None
        failed = True
        continue


    url = f"https://tmapi.transfermarkt.technology/player/{tm_id}/performance-game"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
        "Accept": "application/json",
        "Referer": "https://www.transfermarkt.com/"
    }

    try:
        response = requests.get(url, headers=headers,timeout=10)

        data = response.json()
        performance = data["data"]["performance"]

        hnl_utakmice = [match for match in performance if match["gameInformation"]["competitionId"] == "KR1"
                        and match["statistics"]["generalStatistics"]["participationState"] == "played"
                        and match["gameInformation"]["seasonId"] >= 2006]
        kup_utakmice = [match for match in performance if match["gameInformation"]["competitionId"] == "KRC"
                        and match["statistics"]["generalStatistics"]["participationState"] == "played"
                        and match["gameInformation"]["seasonId"] >= 2013]
        superkup_utakmice = [match for match in performance if match["gameInformation"]["competitionId"] == "HRSC"
                            and match["statistics"]["generalStatistics"]["participationState"] == "played"]
        A_repka_utakmice = [match for match in performance if match["gameInformation"]["competitionTypeId"] in (11,19) 
                            and match["statistics"]["generalStatistics"]["participationState"] == "played"
                            and match["clubsInformation"]["club"]["clubId"] == "3556"]
        hr_utakmice = hnl_utakmice + kup_utakmice + superkup_utakmice
        finale_kupa_utakmice = [match for match in kup_utakmice if match["gameInformation"]["competitionGroupId"] == "FF"]

        klubovi = list(set([match["clubsInformation"]["club"]["clubId"] for match in hnl_utakmice]))
        treneri = list(set([match["clubsInformation"]["club"]["coachId"] for match in hnl_utakmice]))

        A_repka_nastupi = len(A_repka_utakmice)
        hnl_nastupi = len(hnl_utakmice)
        kup_nastupi = len(kup_utakmice)
        superkup_nastupi = len(superkup_utakmice)
        hnl_golovi = sum(match["statistics"]["goalStatistics"]["goalsScoredTotal"] for match in hnl_utakmice)
        finale_kupa_nastupi = len(finale_kupa_utakmice)
        finale_kupa_golovi = sum(match["statistics"]["goalStatistics"]["goalsScoredTotal"] for match in finale_kupa_utakmice)
        superkup_golovi = sum(match["statistics"]["goalStatistics"]["goalsScoredTotal"] for match in superkup_utakmice)
    except Exception as e:
        hnl_utakmice = None
        kup_utakmice = None
        superkup_utakmice = None
        A_repka_utakmice = None
        hr_utakmice = None
        finale_kupa_utakmice = None
        klubovi = None
        treneri = None
        A_repka_nastupi = None
        hnl_nastupi = None
        kup_nastupi = None
        superkup_nastupi = None
        hnl_golovi = None
        finale_kupa_nastupi = None
        finale_kupa_golovi = None
        superkup_golovi = None
        failed = True
        continue


    try:
        response = requests.get(f"{BASE_URL}/players/{tm_id}/achievements",timeout=20)
        data = response.json()
        achievements = data["achievements"]
        if (achievements):
            top_goal_scorer = [a for a in achievements if "top goal scorer" == a["title"].lower()]
            if top_goal_scorer:
                details = top_goal_scorer[0]["details"]
                competitions = [d["competition"] for d in details]
                najbolji_strijelac = sum(1 for c in competitions if c["id"] == "KR1")
            else:
                najbolji_strijelac = 0

            title_winner = [a for a in achievements if a["title"].lower() == "croatian champion"]
            if title_winner:
                hnl_naslovi = title_winner[0]["count"]
            else:
                hnl_naslovi = 0
            cup_winner = [a for a in achievements if a["title"].lower() == "croatian cup winner"]
            if cup_winner:
                kup_naslovi = cup_winner[0]["count"]
            else:
                kup_naslovi = 0
            superkup_winner = [a for a in achievements if a["title"].lower() == "croatian super cup winner"]
            if superkup_winner:
                superkup_naslovi = superkup_winner[0]["count"]
            else:
                superkup_naslovi = 0
        else:
            najbolji_strijelac = 0
            hnl_naslovi = 0
            kup_naslovi = 0
            superkup_naslovi = 0
    except Exception as e:
        najbolji_strijelac = None
        hnl_naslovi = None
        kup_naslovi = None
        superkup_naslovi = None
        failed = True
    
    if failed == True:
        continue
    else:
        player = {
            "tm_id": tm_id,
            "name": name,
            "citizenship": citizenship,
            "nameInHomeCountry": nameInHomeCountry,
            "isRetired": isRetired,
            "marketValue": marketValue,
            "player_slug": player_slug,
            "klubovi": klubovi,
            "treneri": treneri,
            "hnl_nastupi": hnl_nastupi,
            "kup_nastupi": kup_nastupi,
            "superkup_nastupi": superkup_nastupi,
            "A_repka_nastupi": A_repka_nastupi,
            "hnl_golovi": hnl_golovi,
            "finale_kupa_nastupi": finale_kupa_nastupi,
            "finale_kupa_golovi": finale_kupa_golovi,
            "superkup_golovi": superkup_golovi,
            "najbolji_strijelac": najbolji_strijelac,
            "hnl_naslovi": hnl_naslovi,
            "kup_naslovi": kup_naslovi,
            "superkup_naslovi": superkup_naslovi
        }
        print("Rijesen",j)
        j+=1
        players[tm_id] = player
        mistakes.pop(tm_id)
        

with open("data/jsons/all_players_data.json", "w", encoding="utf-8") as f:
    json.dump(players, f, ensure_ascii=False, indent=2)

with open("data/jsons/mistakes_players_data.json", "w", encoding="utf-8") as f:
    json.dump(mistakes, f, ensure_ascii=False, indent=2)