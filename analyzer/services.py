import requests

from django.conf import settings

BASE_URL = "https://api.steampowered.com"


def resolve_steam_id(steam_input):
    steam_input = steam_input.strip().rstrip("/")

    if "/profiles/" in steam_input:
        steam_id = steam_input.split("/profiles/")[-1]
        return steam_id.split("/")[0]

    if "/id/" in steam_input:
        vanity_name = steam_input.split("/id/")[-1]
        vanity_name = vanity_name.split("/")[0]
        return resolve_vanity_url(vanity_name)

    if steam_input.isdigit():
        return steam_input

    return resolve_vanity_url(steam_input)

def resolve_vanity_url(vanity_name):
    url = f"{BASE_URL}/ISteamUser/ResolveVanityURL/v1/"

    params = {
        "key": settings.STEAM_API_KEY,
        "vanityurl": vanity_name,
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()

    data = response.json()

    if data["response"].get("success") == 1:
        return data["response"]["steamid"]

    return None


def get_player_summary(steam_id):
    url = f"{BASE_URL}/ISteamUser/GetPlayerSummaries/v2/"

    params = {
        "key": settings.STEAM_API_KEY,
        "steamids": steam_id,
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()

    data = response.json()
    players = data["response"]["players"]

    if players:
        return players[0]

    return None

def get_owned_games(steam_id):
    url = f"{BASE_URL}/IPlayerService/GetOwnedGames/v1/"

    params = {
        "key": settings.STEAM_API_KEY,
        "steamid": steam_id,
        "include_appinfo": True,
        "include_played_free_games": True,
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()

    data = response.json()

    return data.get("response", {}).get("games", [])