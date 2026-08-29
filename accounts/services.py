from analyzer.services import get_steam_profile_stats


def apply_steam_profile_stats(steam_profile, stats):
    player = stats["player"]

    steam_profile.persona_name = player["personaname"]
    steam_profile.avatar_url = player.get(
        "avatarfull",
        "",
    )

    steam_profile.total_games = stats["total_games"]
    steam_profile.games_played = stats["played_games"]
    steam_profile.total_hours = stats["total_hours"]
    steam_profile.recent_hours = stats["recent_hours"]

    steam_profile.library_played_percent = stats[
        "library_played_percent"
    ]

    steam_profile.average_hours = stats[
        "average_hours"
    ]

    steam_profile.stats_initialized = True

    steam_profile.save()


def refresh_steam_profile(steam_profile):
    stats = get_steam_profile_stats(
        steam_profile.steam_id
    )

    if stats is None:
        return None

    apply_steam_profile_stats(
        steam_profile,
        stats,
    )

    return stats