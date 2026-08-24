import requests

from django.shortcuts import redirect, render

from .services import (
    get_owned_games,
    get_player_summary,
    resolve_steam_id,
)


def home(request):
    steam_input = request.GET.get("steam_input", "").strip()
    error = None

    if steam_input:
        try:
            steam_id = resolve_steam_id(steam_input)

            if steam_id:
                return redirect(
                    "profile_overview",
                    steam_id=steam_id,
                )

            error = "Could not find that Steam profile."

        except requests.RequestException:
            error = "Steam could not be reached. Please try again."

    context = {
        "steam_input": steam_input,
        "error": error,
    }

    return render(request, "analyzer/home.html", context)

def profile_overview(request, steam_id):
    player = None
    games = []
    total_games = 0
    total_hours = 0
    most_played_game = None
    top_games = []
    error = None

    try:
        player = get_player_summary(steam_id)

        if player is None:
            error = "Could not find that Steam profile."

        else:
            games = get_owned_games(steam_id)

            if games:
                total_games = len(games)

                # Steam stores lifetime playtime in minutes.
                total_minutes = sum(
                    game.get("playtime_forever", 0)
                    for game in games
                )

                total_hours = round(total_minutes / 60, 1)

                # Rank the library by lifetime playtime.
                top_games = sorted(
                    games,
                    key=lambda game: game.get(
                        "playtime_forever",
                        0,
                    ),
                    reverse=True,
                )[:5]

                # Convert minutes to hours once for easier template display.
                for game in top_games:
                    game["playtime_hours"] = round(
                        game.get("playtime_forever", 0) / 60,
                        1,
                    )

                most_played_game = top_games[0]

            else:
                error = (
                    "Profile found, but game data is unavailable. "
                    "Make sure your Steam Game Details are public."
                )

    except requests.RequestException:
        error = "Steam could not be reached. Please try again."

    context = {
        "player": player,
        "total_games": total_games,
        "total_hours": total_hours,
        "most_played_game": most_played_game,
        "top_games": top_games,
        "error": error,
    }

    return render(
        request,
        "analyzer/overview.html",
        context,
    )