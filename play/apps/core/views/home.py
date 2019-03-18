import random

from django.shortcuts import render

from apps.core.middleware import profile_required
from apps.core.models import Game
from apps.utils.helpers import generate_game_url


@profile_required
def index(request):
    games = list(
        Game.objects.filter(status=Game.Status.COMPLETE, turn__gte=100)
        .prefetch_related("gamesnake_set")
        .order_by("-created")[:40]
    )
    random.shuffle(games)
    games = [g for g in games if g.gamesnake_set.count() > 1]
    return render(
        request,
        "core/home.html",
        {
            "games": [
                {
                    "url": generate_game_url(g)
                    + "&autoplay=true&hideScoreboard=true&hideMediaControls=true&frameRate=6",
                    "engine_id": g.engine_id,
                }
                for g in games[:4]
            ]
        },
    )
