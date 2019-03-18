from apps.tournament.management.commands.ping_snakes import Command
from apps.tournament.factories import TournamentFactory
from apps.authentication.factories import UserFactory
from apps.core.factories import SnakeFactory
from apps.core.models import Snake
from mock import patch

tournament_factory = TournamentFactory()
snake_factory = SnakeFactory()
user_factory = UserFactory()
command = Command()


@patch.object(Snake, "make_ping_request")
def test_all_healthy(mock_make_ping_request):
    mock_make_ping_request.return_value = 200
    user = user_factory.basic(email="test@example.com", commit=True)
    snake_factory.basic(profile=user.profile, commit=True)
    tournament_factory.basic(url="https://dedsnek.herokuapp.com")
    command.test_all_snakes(only_tournament_snakes=False)
    assert 41 == Snake.objects.filter(healthy=True).count()


@patch.object(Snake, "make_ping_request")
def test_healthy(mock_make_ping_request):
    mock_make_ping_request.return_value = 200
    tournament_factory.basic(url="https://dedsnek.herokuapp.com")
    command.test_all_snakes(only_tournament_snakes=True)
    assert 40 == Snake.objects.filter(healthy=True).count()


@patch.object(Snake, "make_ping_request")
def test_healthy_bad_snake(mock_make_ping_request):
    mock_make_ping_request.return_value = 200
    tournament_factory.basic(url="https://dedsnek.herokuapp.com")
    command.test_all_snakes(only_tournament_snakes=True)
    assert 40 == Snake.objects.filter(healthy=True).count()
    mock_make_ping_request.side_effect = Exception("bad snake")
    command.test_all_snakes(only_tournament_snakes=True)
    assert 40 == Snake.objects.filter(healthy=False).count()


@patch.object(Snake, "make_ping_request")
def test_not_healthy(mock_make_ping_request):
    mock_make_ping_request.return_value = 404
    tournament_factory.basic(url="https://dedsnek.herokuapp.com/someapp")
    command.test_all_snakes(only_tournament_snakes=True)
    assert 40 == Snake.objects.filter(healthy=False).count()
