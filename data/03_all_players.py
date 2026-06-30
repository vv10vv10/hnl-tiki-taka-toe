import requests
from bs4 import BeautifulSoup
import time
import json

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}
hnl_club_slugs = {
    419: "gnk-dinamo-zagreb",
    447: "hnk-hajduk-split",
    144: "hnk-rijeka",
    327: "nk-osijek",
    2362: "slaven-belupo-koprivnica",
    5107: "nk-zagreb",
    599: "nk-varazdin",
    314: "hnk-cibalia-vinkovci",
    223: "hnk-sibenik",
    918: "nk-inker",
    11194: "nk-lokomotiva-zagreb",
    2566: "hnk-zadar",
    999: "nk-istra-1961",
    485: "hnk-hrvatski-dragovoljac",
    420: "rnk-split",
    24575: "hnk-gorica",
    2776: "nk-kamen-ingrad-velika",
    552: "hnk-segesta-sisak",
    34096: "nk-marsonia-1909",
    6087: "nk-medjimurje-cakovec",
    10314: "nk-karlovac-1909",
    11083: "nk-rudes",
    12109: "nk-lucko",
    456: "hnk-vukovar-1991",
    2409: "nk-marsonia-slavonski-brod"
}

seasons = {
    419: 1922,
    447: 1926,
    144: 1962,
    327: 1981,
    2362: 2000,
    5107: 1964,
    599: 1995,
    314: 1998,
    223: 1995,
    918: 1991,
    11194: 2006,
    2566: 1994,
    999: 2002,
    485: 1994,
    420: 2006,
    24575: 2009,
    2776: 2003,
    552: 1991,
    34096: 2011,
    6087: 2004,
    10314: 2006,
    11083: 2006,
    12109: 2006,
    456: 1999,
    2409: 1999
}

players = {}

for id,value in hnl_club_slugs.items():
    for season in range(2004,2027):

        url = f"https://www.transfermarkt.com/{value}/kader/verein/{id}/saison_id/{season}"

        try:
            r = requests.get(url, headers=HEADERS, timeout=20)

            if r.status_code != 200:
                continue

            soup = BeautifulSoup(r.text, "html.parser")

            for a in soup.select("a[href*='/profil/spieler/']"):
                href = a.get("href")

                parts = href.split("/")

                if "spieler" not in parts:
                    continue

                try:
                    player_id = parts[parts.index("spieler") + 1]
                    name = a.get_text(strip=True)

                    players[player_id] = name

                except:
                    continue

            print(f"club {id} season {season} -> total {len(players)} players")

            time.sleep(1)

        except Exception as e:
            print("error:", id, season, e)

print("\nTOTAL UNIQUE PLAYERS:", len(players))

with open("data/jsons/players.json", "w", encoding="utf-8") as f:
    json.dump(players, f, ensure_ascii=False, indent=2)