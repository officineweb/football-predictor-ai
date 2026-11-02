import os
import requests
from dotenv import load_dotenv
load_dotenv()

BASE = "https://v3.football.api-sports.io"
KEY = os.getenv("API_FOOTBALL_KEY")

def api_get(endpoint, params=None):
    if not KEY:
        raise RuntimeError("Set API_FOOTBALL_KEY in .env first")
    r = requests.get(f"{BASE}/{endpoint.lstrip('/')}", headers={"x-apisports-key": KEY},
                     params=params or {}, timeout=30)
    r.raise_for_status()
    data = r.json()
    if data.get("errors"):
        raise RuntimeError(str(data["errors"]))
    return data

def leagues(country=None, season=None):
    params={}
    if country: params["country"]=country
    if season: params["season"]=season
    return api_get("leagues", params)

def fixtures(date=None, league=None, season=None, team=None):
    params={}
    if date: params["date"]=date
    if league: params["league"]=league
    if season: params["season"]=season
    if team: params["team"]=team
    return api_get("fixtures", params)

def fixture_statistics(fixture_id):
    return api_get("fixtures/statistics", {"fixture":fixture_id})

def fixture_players(fixture_id):
    return api_get("fixtures/players", {"fixture":fixture_id})

def odds(fixture_id):
    return api_get("odds", {"fixture":fixture_id})

def predictions(fixture_id):
    return api_get("predictions", {"fixture":fixture_id})
