from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render, redirect
from django.urls import reverse

from apps.core.models import Snake
from apps.leaderboard.models import SnakeLeaderboard


@login_required
def index(request):
    snakes = [
        {
            "id": snake.id,
            "name": snake.name,
            "registered": snake.snakeleaderboard_set.first() is not None,
        }
        for snake in Snake.objects.filter(profile=request.user.profile)
    ]
    return render(request, "leaderboard/snakes.html", {"snakes": snakes})


@login_required
@transaction.atomic
def create(request, snake_id):
    snake = Snake.objects.get(id=snake_id, profile=request.user.profile)
    SnakeLeaderboard.objects.get_or_create(snake=snake)
    return redirect(reverse("leaderboard_snakes"))


@login_required
@transaction.atomic
def delete(request, snake_id):
    snake = Snake.objects.get(id=snake_id, profile=request.user.profile)
    try:
        SnakeLeaderboard.objects.get(snake=snake).delete()
    except SnakeLeaderboard.DoesNotExist:
        pass
    return redirect(reverse("leaderboard_snakes"))
