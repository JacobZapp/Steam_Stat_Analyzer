from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class SignUpForm(UserCreationForm):
    steam_input = forms.CharField(
        max_length=200,
        label="Steam Profile",
        help_text=(
            "Enter your Steam custom URL name, full profile URL, "
            "or SteamID."
        ),
    )

    class Meta:
        model = User
        fields = (
            "username",
            "password1",
            "password2",
            "steam_input",
        )