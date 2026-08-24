from django.urls import path

from . import views


urlpatterns = [
    path("", views.home, name="home"),
    path(
        "profile/<str:steam_id>/",
        views.profile_overview,
        name="profile_overview",
    ),
]