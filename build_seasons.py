# -*- coding: utf-8 -*-

import json
import urllib.request
import time
import random
from urllib.error import HTTPError, URLError

BASE = "https://api.jolpi.ca/ergast/f1"
START_YEAR = 1980
END_YEAR = 2025


def get_json(url: str, retries: int = 6):
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(url, timeout=20) as r:
                return json.loads(r.read().decode("utf-8"))
        except HTTPError as e:
            if e.code == 429:
                wait = 2 + attempt * 2 + random.random()
                print(f"429 en {url} | esperando {wait:.1f}s y reintentando.")
                time.sleep(wait)
                continue
            raise
        except (URLError, TimeoutError):
            wait = 1 + attempt + random.random()
            print(f"Error de red en {url} | esperando {wait:.1f}s y reintentando.")
            time.sleep(wait)
            continue
    raise RuntimeError(f"No se pudo obtener respuesta después de {retries} intentos: {url}")


def get_constructor_champion(year: int):
    url = f"{BASE}/{year}/constructorStandings/1.json"
    data = get_json(url)
    standings = data["MRData"]["StandingsTable"]["StandingsLists"]
    if not standings:
        return None

    s = standings[0]["ConstructorStandings"][0]
    constructor = s["Constructor"]["name"]
    points = float(s["points"])
    wins = int(s["wins"])
    return constructor, points, wins


def get_driver_champion(year: int):
    url = f"{BASE}/{year}/driverStandings/1.json"
    data = get_json(url)
    standings = data["MRData"]["StandingsTable"]["StandingsLists"]
    if not standings:
        return None

    s = standings[0]["DriverStandings"][0]
    driver = s["Driver"]
    return f'{driver["givenName"]} {driver["familyName"]}'


def get_constructor_top2(year: int):
    url = f"{BASE}/{year}/constructorStandings.json"
    data = get_json(url)
    standings = data["MRData"]["StandingsTable"]["StandingsLists"]
    if not standings:
        return None

    rows = standings[0]["ConstructorStandings"]
    if len(rows) < 2:
        return None

    first = rows[0]
    second = rows[1]

    p1_name = first["Constructor"]["name"]
    p1_points = float(first["points"])
    p2_name = second["Constructor"]["name"]
    p2_points = float(second["points"])
    gap = round(p1_points - p2_points, 1)

    return {
        "p1Constructor": p1_name,
        "p1Points": p1_points,
        "p2Constructor": p2_name,
        "p2Points": p2_points,
        "pointsGap": gap,
    }


def get_races_in_season(year: int):
    url = f"{BASE}/{year}.json"
    data = get_json(url)
    total = int(data["MRData"]["total"])
    return total


def get_unique_winning_constructors(year: int):
    url = f"{BASE}/{year}/results/1.json?limit=100"
    data = get_json(url)
    races = data["MRData"]["RaceTable"]["Races"]
    if not races:
        return 0

    winners = set()
    for race in races:
        results = race.get("Results", [])
        if not results:
            continue
        constructor = results[0]["Constructor"]["name"]
        winners.add(constructor)

    return len(winners)


def build():
    seasons = []

    # bloque resumen fijo
    seasons.append({
        "year": 1950,
        "type": "summary",
        "label": "1950–1979",
        "title": "Era Fundacional (1950–1979)",
        "constructorChampion": "N/A",
        "dominance": None,
        "highlights": [
            "Nace el campeonato mundial (1950).",
            "Se consolidan los equipos y tecnologías base del deporte.",
            "Surgen leyendas y rivalidades fundacionales."
        ]
    })

    for year in range(START_YEAR, END_YEAR + 1):
        print(f"Procesando {year}...")

        champ = get_constructor_champion(year)
        time.sleep(0.4 + random.random() * 0.4)
        if champ is None:
            continue

        constructor, points, team_wins = champ

        driver_champion = get_driver_champion(year)
        time.sleep(0.4 + random.random() * 0.4)

        top2 = get_constructor_top2(year)
        time.sleep(0.4 + random.random() * 0.4)

        races = get_races_in_season(year)
        time.sleep(0.4 + random.random() * 0.4)

        unique_winners = get_unique_winning_constructors(year)
        time.sleep(0.4 + random.random() * 0.4)

        dominance = team_wins / races if races else None

        seasons.append({
            "year": year,
            "constructorChampion": constructor,
            "driverChampion": driver_champion,
            "champPoints": points,
            "teamWins": team_wins,
            "racesInSeason": races,
            "dominance": round(dominance, 4) if dominance is not None else None,
            "p2Constructor": top2["p2Constructor"] if top2 else None,
            "p2Points": top2["p2Points"] if top2 else None,
            "pointsGap": top2["pointsGap"] if top2 else None,
            "uniqueWinningConstructors": unique_winners,
            "title": f"Temporada {year}",
            "highlights": []
        })

    with open("client/data/seasons.json", "w", encoding="utf-8") as f:
        json.dump(seasons, f, ensure_ascii=False, indent=2)

    print("Listo: data/seasons.json generado")


if __name__ == "__main__":
    build()