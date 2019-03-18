from django.shortcuts import render

from apps.leaderboard.models import SnakeLeaderboard
from apps.leaderboard.presenters import SnakeLeaderboardPresenter


def index(request):
    leaderboard = SnakeLeaderboard.ranked()
    return render(
        request,
        "leaderboard/index.html",
        {
            "leaderboard": [SnakeLeaderboardPresenter(l) for l in leaderboard],
            "user": request.user,
        },
    )
