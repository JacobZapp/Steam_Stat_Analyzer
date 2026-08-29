import requests

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from accounts.models import SteamProfile
from accounts.services import refresh_steam_profile

from .services import get_steam_profile_stats

def home(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    return redirect("login")

@login_required
def profile_overview(request, steam_id):
    context = {
        "player": None,
        "total_games": 0,
        "total_hours": 0,
        "most_played_game": None,
        "top_games": [],

        "played_games": 0,
        "unplayed_games": 0,
        "library_played_percent": 0,
        "average_hours": 0,

        "recent_games": [],
        "recent_hours": 0,

        "error": None,
    }

    try:
        stored_profile = SteamProfile.objects.filter(
            steam_id=steam_id
        ).first()

        if stored_profile:
            stats = refresh_steam_profile(
                stored_profile
            )

        else:
            stats = get_steam_profile_stats(
                steam_id
            )

        if stats is None:
            context["error"] = (
                "Could not find that Steam profile."
            )

        else:
            context.update(stats)

            if not stats["games"]:
                context["error"] = (
                    "Profile found, but game data is unavailable. "
                    "Make sure your Steam Game Details are public."
                )

    except requests.RequestException:
        context["error"] = (
            "Steam could not be reached. Please try again."
        )

    return render(
        request,
        "analyzer/overview.html",
        context,
        )


@login_required
def dashboard(request):
    uninitialized_profiles = SteamProfile.objects.filter(
        stats_initialized=False
    )

    for profile in uninitialized_profiles:
        try:
            refresh_steam_profile(profile)

        except requests.RequestException:
            pass

    search = request.GET.get("search", "").strip()
    sort = request.GET.get("sort", "hours")

    profiles = SteamProfile.objects.select_related("user").all()

    if search:
        profiles = profiles.filter(
            persona_name__icontains=search
        )

    if sort == "games":
        profiles = profiles.order_by(
            "-total_games"
        )

    elif sort == "played":
        profiles = profiles.order_by(
            "-games_played"
        )

    elif sort == "recent":
        profiles = profiles.order_by(
            "-recent_hours"
        )

    elif sort == "library":
        profiles = profiles.order_by(
            "-library_played_percent"
        )

    else:
        profiles = profiles.order_by(
            "-total_hours"
        )

    context = {
        "profiles": profiles,
        "search": search,
        "sort": sort,
    }

    return render(
        request,
        "analyzer/dashboard.html",
        context,
    )