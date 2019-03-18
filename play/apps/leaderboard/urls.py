from django.urls import path
from apps.leaderboard import views
from util.routing import method_dispatch as route

urlpatterns = [
    path("leaderboard/", route(GET=views.leaderboard.index), name="leaderboard"),
    path(
        "leaderboard/snakes/", route(GET=views.snakes.index), name="leaderboard_snakes"
    ),
    path(
        "leaderboard/snakes/<snake_id>/",
        route(POST=views.snakes.create, DELETE=views.snakes.delete),
        name="leaderboard_snakes_action",
    ),
]
