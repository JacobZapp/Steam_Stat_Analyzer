import requests

from django.shortcuts import render

from .services import get_player_summary, resolve_steam_id


def home(request):
    steam_input = request.GET.get("steam_input", "").strip()

    player = None
    error = None

    if steam_input:
        try:
            steam_id = resolve_steam_id(steam_input)

            if steam_id:
                player = get_player_summary(steam_id)

                if player is None:
                    error = "Steam profile could not be found."
            else:
                error = "Steam profile could not be found."

        except requests.RequestException:
            error = "Steam could not be reached. Please try again."

    context = {
        "steam_input": steam_input,
        "player": player,
        "error": error,
    }

    return render(request, "analyzer/home.html", context)