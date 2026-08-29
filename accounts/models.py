from django.contrib.auth.models import User
from django.db import models


class SteamProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="steam_profile",
    )

    steam_id = models.CharField(
        max_length=17,
        unique=True,
    )

    persona_name = models.CharField(
        max_length=100,
    )

    avatar_url = models.URLField(
        blank=True,
    )

    total_games = models.PositiveIntegerField(
        default=0,
    )

    games_played = models.PositiveIntegerField(
        default=0,
    )

    total_hours = models.FloatField(
        default=0,
    )

    recent_hours = models.FloatField(
        default=0,
    )

    library_played_percent = models.FloatField(
        default=0,
    )

    average_hours = models.FloatField(
        default=0,
    )

    stats_initialized = models.BooleanField(
        default=False,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return f"{self.user.username} - {self.persona_name}"