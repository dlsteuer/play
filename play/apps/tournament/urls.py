from django.urls import path

from apps.tournament import views as tournament_views
from util.routing import method_dispatch as route

urlpatterns = [
    # NOTE: Commented routes will be enabled in a future update after the tournament
    path(
        "team/",
        # route(GET=tournament_views.team.index, PUT=tournament_views.team.update),
        route(GET=tournament_views.team.index),
    ),
    # path(
    #     "team/new/",
    #     route(GET=tournament_views.team.new, POST=tournament_views.team.new),
    # ),
    # path(
    #     "team/edit/",
    #     route(GET=tournament_views.team.edit),
    # ),
    path("team/members/", route(GET=tournament_views.members.index)),
    # path(
    #     "team/members/new/",
    #     route(GET=tournament_views.members.new, POST=tournament_views.members.new),
    # ),
    # path(
    #     "team/members/<id>/",
    #     route(DELETE=tournament_views.members.delete),
    # ),
    path(
        "tournaments/", route(GET=tournament_views.tournament.index), name="tournaments"
    ),
    path(
        "tournament/new/",
        route(
            GET=tournament_views.tournament.new, POST=tournament_views.tournament.new
        ),
        name="new_tournament",
    ),
    path(
        "tournament/<tournament_id>/edit/",
        route(
            GET=tournament_views.tournament.edit, POST=tournament_views.tournament.edit
        ),
        name="edit_tournament",
    ),
    path(
        "tournament/<tournament_id>/bracket/new/",
        route(
            GET=tournament_views.tournament_bracket.new,
            POST=tournament_views.tournament_bracket.new,
        ),
        name="new_tournament_bracket",
    ),
    path(
        "tournament/<tournament_id>/current_game/",
        route(
            GET=tournament_views.tournament.show_current_game,
            POST=tournament_views.tournament.cast_current_game,
        ),
        name="current_tournament_game",
    ),
    path(
        "tournament/<tournament_id>/commentator/",
        route(GET=tournament_views.tournament.commentator_details),
        name="tournament_commentator_details",
    ),
    path(
        "tournament/<tournament_id>/allTeams/",
        route(GET=tournament_views.all_teams.show),
        name="tournament_teams_list",
    ),
    path(
        "tournament/<tournament_id>/compete/",
        route(
            GET=tournament_views.tournament_snake.compete,
            POST=tournament_views.tournament_snake.compete,
            PUT=tournament_views.tournament_snake.compete,
        ),
        name="compete_tournament",
    ),
    path(
        "tournament/snake/<tournament_snake_id>/edit/",
        route(
            GET=tournament_views.tournament_snake.edit,
            POST=tournament_views.tournament_snake.edit,
            PUT=tournament_views.tournament_snake.edit,
        ),
        name="edit_tournament_snake",
    ),
    path(
        "tournament/snake/<tournament_snake_id>/delete/",
        route(
            GET=tournament_views.tournament_snake.delete,
            POST=tournament_views.tournament_snake.delete,
            PUT=tournament_views.tournament_snake.delete,
        ),
        name="delete_tournament_snake",
    ),
    path(
        "tournament/bracket/<bracket_id>/",
        route(GET=tournament_views.tournament_bracket.show),
        name="tournament_bracket",
    ),
    path(
        "tournament/bracket/<bracket_id>/edit/",
        route(
            GET=tournament_views.tournament_bracket.edit,
            POST=tournament_views.tournament_bracket.edit,
            PUT=tournament_views.tournament_bracket.edit,
        ),
        name="edit_tournament_bracket",
    ),
    path(
        "tournament/bracket/<bracket_id>/csv/",
        route(GET=tournament_views.tournament_bracket.show_csv),
        name="tournament_bracket_csv",
    ),
    path(
        "tournament/bracket/<bracket_id>/tree/",
        route(GET=tournament_views.tournament_bracket.tree),
        name="tournament_bracket_tree",
    ),
    path(
        "tournament/bracket/<bracket_id>/set-casting/",
        route(GET=tournament_views.tournament_bracket.cast_page),
        name="cast_tournament_bracket",
    ),
    path(
        "tournament/bracket/<bracket_id>/create/next/round/",
        route(GET=tournament_views.tournament_bracket.create_next_round),
        name="tournament_bracket_create_next_round",
    ),
    path(
        "tournament/bracket/<bracket_id>/update/games/",
        route(GET=tournament_views.tournament_bracket.update_game_statuses),
        name="tournament_bracket_update_game_statuses",
    ),
    path(
        "tournament/bracket/<bracket_id>/heat/<heat_id>/create_game/",
        route(
            GET=tournament_views.tournament_bracket.create_game,
            POST=tournament_views.tournament_bracket.create_game,
        ),
        name="tournament_bracket_create_next_round_heat",
    ),
    path(
        "tournament/bracket/<bracket_id>/heat/<heat_id>/game/<heat_game_number>/delete/",
        route(GET=tournament_views.tournament_bracket.delete_game),
        name="tournament_bracket_delete_round_heat_game",
    ),
    path(
        "heat/<heat_id>/game/<heat_game_number>/",
        route(GET=tournament_views.tournament_bracket.run_heat_game),
        name="tournament_bracket_heat_game",
    ),
    path(
        "tournament/admin/",
        route(GET=tournament_views.admin.index),
        name="tournament_admin",
    ),
    path(
        "tournament/admin/teams/",
        route(GET=tournament_views.admin.find_teams),
        name="tournament_admin_find_teams",
    ),
    path(
        "tournament/admin/teams/new/",
        route(
            GET=tournament_views.admin.new_team, POST=tournament_views.admin.update_team
        ),
        name="new_tournament_admin_team",
    ),
    path(
        "tournament/admin/teams/<team_id>/",
        route(
            GET=tournament_views.admin.edit_team,
            POST=tournament_views.admin.update_team,
        ),
        name="tournament_admin_team",
    ),
    path(
        "tournament/admin/users/",
        route(GET=tournament_views.admin.users),
        name="tournament_users",
    ),
    path(
        "tournament/admin/users/info/",
        route(GET=tournament_views.admin.user_info),
        name="tournament_user",
    ),
    path(
        "tournament/admin/users/snakes/",
        route(GET=tournament_views.admin.snakes),
        name="tournament_user_snakes",
    ),
    path(
        "tournament/admin/users/snakes/status/<snake_id>/",
        route(GET=tournament_views.admin.snake_status),
        name="tournament_user_snake_status",
    ),
]
