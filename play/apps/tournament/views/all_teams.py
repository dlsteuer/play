from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from apps.authentication.decorators import admin_required
from apps.tournament.models import Tournament
from django.core.exceptions import ObjectDoesNotExist
import logging

logger = logging.getLogger(__name__)


def create_view_model(tournament_id):
    tournament = Tournament.objects.filter(id=tournament_id)
    if tournament.count() == 0:
        return {
            "brackets": [
                {"name": "Could not find tournament with id: " + str(tournament_id)}
            ]
        }

    result = {"brackets": []}
    brackets = tournament.get().brackets
    for bracket in brackets:
        current_bracket = {"name": bracket.name, "teams": []}
        result["brackets"].append(current_bracket)
        for snake in bracket.snakes.all():
            try:
                current_bracket.get("teams").append(
                    {
                        # TODO: This is really weird, we should be registering teams in tournaments, not just snakes
                        "name": snake.profile.team_set.first().name,
                        "status": ("healthy" if snake.healthy else "unhealthy"),
                    }
                )
            except ObjectDoesNotExist:
                snake_user_id = snake.profile.user.id
                logger.warning(
                    f"Couldn't find team for snake: {snake}, snake.user.id: {snake_user_id}"
                )
        current_bracket.get("teams").sort(key=lambda x: x.get("name"))

    return result


@login_required
@admin_required
def show(request, tournament_id):
    return render(request, "all_teams/show.html", create_view_model(tournament_id))
