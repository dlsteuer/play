from apps.authentication.factories import UserFactory
from apps.core.factories import SnakeFactory
from apps.tournament.factories import TeamFactory, TournamentFactory
from apps.tournament.views.all_teams import create_view_model
from apps.tournament.management.commands.ping_snakes import Command
from apps.core.models.snake import Snake
from mock import patch

user_factory = UserFactory()
team_factory = TeamFactory()
snake_factory = SnakeFactory()
tournament_factory = TournamentFactory()
ping_checker = Command()


def test_index(client):
    user_factory.login_as(client, "codeallthethingz@example.com", is_admin=True)
    tournament = tournament_factory.basic(url="https://dedsnek.herokuapp.com")
    response = client.get("/tournament/" + str(tournament.id) + "/allTeams/")
    assert response.status_code == 200


def test_index_no_tournament(client):
    user_factory.login_as(client, "codeallthethingz@example.com", is_admin=True)
    response = client.get("/tournament/" + str("-23342344") + "/allTeams/")
    assert response.status_code == 200
    assert "Could not find tournament" in str(response.content)


def test_create_view_model_no_brackets(client):
    tournament = tournament_factory.createEmpty()
    model = create_view_model(tournament.id)
    assert model == {"brackets": []}


def test_create_view_model(client):
    tournament = tournament_factory.basic(url="https://dedsnek.herokuapp.com")
    model = create_view_model(tournament.id)

    firstBracket = model.get("brackets")[0]
    assert firstBracket.get("name") == "Beginner"
    assert len(firstBracket.get("teams")) == 18
    assert firstBracket.get("teams")[0].get("name") == "team 22"
    assert firstBracket.get("teams")[0].get("status") == "unhealthy"
    assert firstBracket.get("teams")[17].get("name") == "team 39"

    secondBracket = model.get("brackets")[1]
    assert secondBracket.get("name") == "Intermediate"
    assert len(secondBracket.get("teams")) == 14

    thirdBracket = model.get("brackets")[2]
    assert thirdBracket.get("name") == "Advanced"
    assert len(thirdBracket.get("teams")) == 8
    assert thirdBracket.get("teams")[0].get("name") == "team 0"
    assert thirdBracket.get("teams")[7].get("name") == "team 7"


@patch.object(Snake, "make_ping_request")
def test_all_unhealthy(mock_make_ping_request):
    mock_make_ping_request.return_value = 500
    tournament = tournament_factory.basic(url="https://dedsnek.herokuapp.com")
    ping_checker.test_all_snakes(only_tournament_snakes=True)
    model = create_view_model(tournament.id)
    assertTeamsStatus(model=model, status="unhealthy")


@patch.object(Snake, "make_ping_request")
def test_all_healthy(mock_make_ping_request):
    mock_make_ping_request.return_value = 200
    tournament = tournament_factory.basic(url="https://dedsnek.herokuapp.com")
    ping_checker.test_all_snakes(only_tournament_snakes=True)
    model = create_view_model(tournament.id)
    assertTeamsStatus(model=model, status="healthy")


def assertTeamsStatus(model, status):
    for bracket in model.get("brackets"):
        for team in bracket.get("teams"):
            assert team.get("status") == status
