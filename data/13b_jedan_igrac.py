import requests
from bs4 import BeautifulSoup

tm_id = 95438

# osobni podaci
BASE_URL = "https://transfermarkt-api.fly.dev"
response = requests.get(f"{BASE_URL}/players/{tm_id}/profile")
data = response.json()
name=data["name"]
citizenship=data["citizenship"]
nameInHomeCountry=data.get("nameInHomeCountry") or name
height=data["height"]
isRetired=data["isRetired"]
marketValue=data["marketValue"]
player_slug=data["url"].split("/")[3]
#rijesit dateOfBirth



url = f"https://tmapi.transfermarkt.technology/player/{tm_id}/performance-game"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
    "Accept": "application/json",
    "Referer": "https://www.transfermarkt.com/"
}

response = requests.get(url, headers=headers)

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

klubovi = set([match["clubsInformation"]["club"]["clubId"] for match in hnl_utakmice])
treneri = set([match["clubsInformation"]["club"]["coachId"] for match in hnl_utakmice])

A_repka_nastupi = len(A_repka_utakmice)
hnl_nastupi = len(hnl_utakmice)
kup_nastupi = len(kup_utakmice)
superkup_nastupi = len(superkup_utakmice)
hnl_golovi = sum(match["statistics"]["goalStatistics"]["goalsScoredTotal"] for match in hnl_utakmice)
finale_kupa_nastupi = len(finale_kupa_utakmice)
finale_kupa_golovi = sum(match["statistics"]["goalStatistics"]["goalsScoredTotal"] for match in finale_kupa_utakmice)
superkup_golovi = sum(match["statistics"]["goalStatistics"]["goalsScoredTotal"] for match in superkup_utakmice)


BASE_URL = "https://transfermarkt-api.fly.dev"
response = requests.get(f"{BASE_URL}/players/{tm_id}/achievements")
data = response.json()
achievements = data["achievements"]

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

player = {
    "tm_id": tm_id,
    "name": name,
    "citizenship": citizenship,
    "nameInHomeCountry": nameInHomeCountry,
    "height": height,
    "isRetired": isRetired,
    "marketValue": marketValue,
    "player_slug": player_slug,
    "klubovi": list(klubovi),
    "treneri": list(treneri),
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

print(player)