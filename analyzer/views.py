from django.shortcuts import render


def home(request):
    steam_input = request.GET.get("steam_input")

    return render(
        request,
        "analyzer/home.html",
        {"steam_id": steam_input},
    )