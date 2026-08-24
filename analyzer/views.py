import requests

from django.shortcuts import render

from .services import (
    get_owned_games,
    get_player_summary,
    resolve_steam_id,
)


def home(request):
    steam_input = request.GET.get("steam_input", "").strip()

    player = None
    games = []
    total_games = 0
    total_hours = 0
    most_played_game = None
    top_games = []
    error = None

    if steam_input:
        try:
            steam_id = resolve_steam_id(steam_input)

            if not steam_id:
                error = "Could not find that Steam profile."

            else:
                player = get_player_summary(steam_id)

                if player is None:
                    error = "Could not find that Steam profile."

                else:
                    games = get_owned_games(steam_id)

                    if games:
                        total_games = len(games)

                        # Steam returns playtime in minutes, so convert it to hours.
                        total_minutes = sum(
                            game.get("playtime_forever", 0)
                            for game in games
                        )

                        total_hours = round(total_minutes / 60, 1)

                        # Sort highest-to-lowest by lifetime playtime.
                        top_games = sorted(
                            games,
                            key=lambda game: game.get("playtime_forever", 0),
                            reverse=True,
                        )[:5]

                        most_played_game = top_games[0]

                        # Add an easier-to-display hours value to each top game.
                        for game in top_games:
                            game["playtime_hours"] = round(
                                game.get("playtime_forever", 0) / 60,
                                1,
                            )

                    else:
                        error = (
                            "Profile found, but game data is unavailable. "
                            "Make sure your Steam Game Details are public."
                        )

        except requests.RequestException as exc:
            error = f"Steam API error: {exc}"

    context = {
        "steam_input": steam_input,
        "player": player,
        "total_games": total_games,
        "total_hours": total_hours,
        "most_played_game": most_played_game,
        "top_games": top_games,
        "error": error,
    }

    return render(request, "analyzer/home.html", context)