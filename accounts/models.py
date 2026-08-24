from django.contrib.auth.models import User
from django.db import models


class SteamProfile(models.Model):
    user = models.OneToOneField( #made sure to make it so one account can only have one steam profile and vice versa
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

    def __str__(self):
        return f"{self.user.username} - {self.persona_name}"