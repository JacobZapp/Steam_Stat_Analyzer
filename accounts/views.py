import requests

from django.contrib.auth import login
from django.shortcuts import redirect, render

from analyzer.services import (
    get_player_summary,
    resolve_steam_id,
)

from .forms import SignUpForm
from .models import SteamProfile


def signup(request):
    if request.method == "POST": # essentially means giving info that makes a change to something
        form = SignUpForm(request.POST)

        # Thank you Django for doing all of this validation for me. I would have had to do all of this manually otherwise.
        if form.is_valid():
            steam_input = form.cleaned_data["steam_input"]

            try:
                steam_id = resolve_steam_id(steam_input)

                if not steam_id:
                    form.add_error(
                        "steam_input",
                        "Could not find that Steam profile.",
                    )

                elif SteamProfile.objects.filter(
                    steam_id=steam_id
                ).exists():
                    form.add_error(
                        "steam_input",
                        "That Steam profile is already linked to an account.",
                    )

                else:
                    player = get_player_summary(steam_id)

                    if not player:
                        form.add_error(
                            "steam_input",
                            "Could not load that Steam profile.",
                        )

                    else:
                        user = form.save()

                        SteamProfile.objects.create(
                            user=user,
                            steam_id=steam_id,
                            persona_name=player["personaname"],
                            avatar_url=player.get("avatarfull", ""),
                        )

                        login(request, user)

                        return redirect("dashboard")

            except requests.RequestException:
                form.add_error(
                    "steam_input",
                    "Steam could not be reached. Please try again.",
                )

    else:
        form = SignUpForm()

    return render(
        request,
        "accounts/signup.html",
        {"form": form},
    )