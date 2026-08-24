import requests
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .services import (
    get_owned_games,
    get_player_summary,
    get_recently_played_games,
    resolve_steam_id,
)


def home(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    return redirect("login")

def profile_overview(request, steam_id):
    player = None
    games = []
    total_games = 0
    total_hours = 0
    most_played_game = None
    top_games = []
    error = None
    played_games = 0
    unplayed_games = 0
    library_played_percent = 0
    average_hours = 0

    recent_games = []
    recent_hours = 0

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

                #better than using all games cuz the average would skewed with games that never got played
                if played_games > 0:
                    average_hours = round(total_hours / played_games, 1,
                                          )

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

                # A game counts as "played" if Steam reports any lifetime playtime.
                played_games = sum(
                    1
                    for game in games
                    if game.get("playtime_forever", 0) > 0
                )

                unplayed_games = total_games - played_games

                if total_games > 0:
                    library_played_percent = round(
                        (played_games / total_games) * 100,
                        1,
                    )

            else:
                error = (
                    "Profile found, but game data is unavailable. "
                    "Make sure your Steam Game Details are public."
                )
        recent_games = get_recently_played_games(steam_id)

        if recent_games:
            recent_minutes = sum(
                game.get("playtime_2weeks", 0)
                for game in recent_games
            )

            recent_hours = round(recent_minutes / 60, 1)

            for game in recent_games:
                game["recent_hours"] = round(
                    game.get("playtime_2weeks", 0) / 60,
                    1,
                )

    except requests.RequestException:
        error = "Steam could not be reached. Please try again."

    context = {
    "player": player,
    "total_games": total_games,
    "total_hours": total_hours,
    "most_played_game": most_played_game,
    "top_games": top_games,

    "played_games": played_games,
    "unplayed_games": unplayed_games,
    "library_played_percent": library_played_percent,
    "average_hours": average_hours,

    "recent_games": recent_games,
    "recent_hours": recent_hours,

    "error": error,
}

    return render(
        request,
        "analyzer/overview.html",
        context,
    )

@login_required
def dashboard(request):
    from accounts.models import SteamProfile

    search = request.GET.get("search", "").strip()

    profiles = SteamProfile.objects.select_related("user").all()

    if search:
        profiles = profiles.filter(
            persona_name__icontains=search
        )

    context = {
        "profiles": profiles,
        "search": search,
    }

    return render(
        request,
        "analyzer/dashboard.html",
        context,
    )
