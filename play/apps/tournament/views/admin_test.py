import json
from datetime import timedelta, datetime

from apps.authentication.factories import UserFactory
from apps.core.factories import SnakeFactory
from apps.tournament.factories import TournamentFactory, TeamFactory
from apps.tournament.models import TournamentBracket

user_factory = UserFactory()
tournament_factory = TournamentFactory()
snake_factory = SnakeFactory()
team_factory = TeamFactory()


def test_index(client):
    user_factory.login_as(client, "dlsteuer@example.com", is_admin=True)
    response = client.get("/tournament/admin/")
    assert response.status_code == 200


def test_find_teams(client):
    user = user_factory.login_as(client, "dlsteuer@example.com", is_admin=True)
    team = team_factory.basic(user)
    response = client.get(f"/tournament/admin/teams/?q={team.name}")
    assert response.status_code == 200
    j = json.loads(response.content)
    assert len(j) == 1
    assert j[0]["text"] == team.name


def test_new_team(client):
    user_factory.login_as(client, "dlsteuer@example.com", is_admin=True)
    response = client.get("/tournament/admin/teams/new/")
    assert response.status_code == 200


def test_edit_team(client):
    user = user_factory.login_as(client, "dlsteuer@example.com", is_admin=True)
    team = team_factory.basic(user)
    response = client.get(f"/tournament/admin/teams/{team.id}/")
    assert response.status_code == 200
    assert response.context[-1]["form"] is not None


def test_update_team_new_team(client):
    user = user_factory.login_as(client, "dlsteuer@example.com", is_admin=True)
    snake = snake_factory.basic(commit=True, profile=user.profile)
    t = tournament_factory.createEmpty()
    t.date = datetime.now() + timedelta(days=1)
    t.save()
    tb = TournamentBracket.objects.create(tournament=t)
    response = client.post(
        "/tournament/admin/teams/new/",
        {
            "name": "Test Team",
            "description": "Description",
            "snakes": snake.id,
            "users": user.id,
            "tournament": f"{t.id}/{tb.id}",
        },
    )
    assert response.status_code == 302


def test_update_team_new_team_with_errors(client):
    user_factory.login_as(client, "dlsteuer@example.com", is_admin=True)
    response = client.post("/tournament/admin/teams/new/", {})
    assert response.status_code == 200
    assert response.context[-1]["form"].errors is not None


def test_update_team_existing_team(client):
    user = user_factory.login_as(client, "dlsteuer@example.com", is_admin=True)
    team = team_factory.basic(user)
    snake = snake_factory.basic(commit=True, profile=user.profile)
    t = tournament_factory.createEmpty()
    t.date = datetime.now() + timedelta(days=1)
    t.save()
    tb = TournamentBracket.objects.create(tournament=t)
    response = client.post(
        f"/tournament/admin/teams/{team.id}/",
        {
            "name": "Test Team",
            "description": "Description",
            "snakes": snake.id,
            "users": user.id,
            "tournament": f"{t.id}/{tb.id}",
        },
    )
    print(response.context)
    assert response.status_code == 302
