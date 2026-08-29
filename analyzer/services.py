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


def get_recently_played_games(steam_id):
    url = f"{BASE_URL}/IPlayerService/GetRecentlyPlayedGames/v1/"

    params = {
        "key": settings.STEAM_API_KEY,
        "steamid": steam_id,
        "count": 0,
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()

    data = response.json()

    return data.get("response", {}).get("games", [])

def get_steam_profile_stats(steam_id):
    player = get_player_summary(steam_id)

    if player is None:
        return None

    games = get_owned_games(steam_id)
    recent_games = get_recently_played_games(steam_id)

    total_games = 0
    played_games = 0
    unplayed_games = 0

    total_hours = 0
    library_played_percent = 0
    average_hours = 0

    top_games = []
    most_played_game = None

    recent_hours = 0

    if games:
        total_games = len(games)

        played_games = sum(
            1
            for game in games
            if game.get("playtime_forever", 0) > 0
        )

        unplayed_games = total_games - played_games

        library_played_percent = round(
            (played_games / total_games) * 100,
            1,
        )

        # Steam reports lifetime playtime in minutes.
        total_minutes = sum(
            game.get("playtime_forever", 0)
            for game in games
        )

        total_hours = round(
            total_minutes / 60,
            1,
        )

        if played_games > 0:
            average_hours = round(
                total_hours / played_games,
                1,
            )

        top_games = sorted(
            games,
            key=lambda game: game.get(
                "playtime_forever",
                0,
            ),
            reverse=True,
        )[:5]

        for game in top_games:
            game["playtime_hours"] = round(
                game.get("playtime_forever", 0) / 60,
                1,
            )

        most_played_game = top_games[0]

    if recent_games:
        recent_minutes = sum(
            game.get("playtime_2weeks", 0)
            for game in recent_games
        )

        recent_hours = round(
            recent_minutes / 60,
            1,
        )

        for game in recent_games:
            game["recent_hours"] = round(
                game.get("playtime_2weeks", 0) / 60,
                1,
            )

    return {
        "player": player,
        "games": games,

        "total_games": total_games,
        "played_games": played_games,
        "unplayed_games": unplayed_games,

        "total_hours": total_hours,
        "library_played_percent": library_played_percent,
        "average_hours": average_hours,

        "top_games": top_games,
        "most_played_game": most_played_game,

        "recent_games": recent_games,
        "recent_hours": recent_hours,
    }