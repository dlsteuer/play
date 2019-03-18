from django.shortcuts import redirect
from django.urls import path

from apps.core.views import game, home, profile, profiles, snake, stats
from util.routing import method_dispatch as route


urlpatterns = [
    path(
        "settings/",
        route(GET=profile.edit, PUT=profile.update, DELETE=profile.delete),
        name="settings",
    ),
    path("u/by-games-snake/<game_snake_id>", route(GET=profiles.show_by_game_snake)),
    path("u/<username>/", route(GET=profiles.show), name="u"),
    path("", route(GET=home.index), name="home"),
    path("s/new/", route(GET=snake.new, POST=snake.create), name="new_snake"),
    path("s/<snake_id>/", route(GET=snake.show, DELETE=snake.delete), name="snake"),
    path(
        "s/<snake_id>/edit/", route(GET=snake.edit, PUT=snake.update), name="snake_edit"
    ),
    path("g/new/", route(GET=game.new, POST=game.create), name="new_game"),
    path("g/snake-autocomplete/", route(GET=game.snake_autocomplete)),
    path("g/snake-info/", route(GET=game.snake_info)),
    path("g/random-public-snake/", route(GET=game.random_public_snake)),
    path("g/<engine_id>/", route(GET=game.show), name="game"),
    path("g/<engine_id>/gif", route(GET=game.show_gif), name="game_gif"),
    path("stats/", route(GET=stats.show), name="stats"),
    # Old redirects
    path("games/new/", lambda req: redirect("new_game")),
    path("games/<engine_id>/", lambda req, engine_id: redirect("game", engine_id)),
]
