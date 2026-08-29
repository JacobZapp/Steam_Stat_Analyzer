import requests

from django.contrib.auth import login
from django.shortcuts import redirect, render

from .services import apply_steam_profile_stats

from analyzer.services import (
    get_steam_profile_stats,
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
                    stats = get_steam_profile_stats(
                        steam_id
                    )

                    if stats is None:
                        form.add_error(
                            "steam_input",
                            "Could not find that Steam profile.",
                        )

                    else:
                        user = form.save()

                        steam_profile = SteamProfile.objects.create(
                            user=user,
                            steam_id=steam_id,
                        )

                        apply_steam_profile_stats(
                            steam_profile,
                            stats,
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