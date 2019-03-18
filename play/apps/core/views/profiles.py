from django.shortcuts import render, redirect
from django.http import Http404
from apps.core.models import Profile, GameSnake
from apps.core.middleware import profile_required


@profile_required
def show(request, username):
    # Case-insensitive lookup, redirects to correct URL
    profile = Profile.objects.get(user__username__iexact=username)
    if profile.username != username:
        return redirect("u", profile.username)

    games = (
        profile.games.watchable()
        .order_by("-created")
        .prefetch_related("gamesnake_set__snake")
        .distinct()[:10]
    )
    return render(
        request, "core/profiles/show.html", {"profile": profile, "games": games}
    )


@profile_required
def show_by_game_snake(request, game_snake_id):
    try:
        game_snake = GameSnake.objects.get(id=game_snake_id)
    except GameSnake.DoesNotExist:
        raise Http404
    return redirect("u", game_snake.snake.profile.username)
