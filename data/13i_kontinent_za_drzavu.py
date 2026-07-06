import json

with open("data/jsons/all_countries.json", "r", encoding="utf-8") as f:
    countries = json.load(f)
with open("data/jsons/countries_with_confederations.json", "r", encoding="utf-8") as f:
    countries_with_conf = json.load(f)

countries2 = {}

for c in countries:
    if c not in countries_with_conf.keys():
        print(c)
    else:
        countries2[c] = countries_with_conf.get(c)

with open("data/jsons/all_countries.json", "w", encoding="utf-8") as f:
    json.dump(countries2, f, ensure_ascii=False, indent=2)