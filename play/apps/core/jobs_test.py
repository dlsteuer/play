import uuid
import mock
from apps.authentication.factories import UserFactory
from apps.core.models import Game, GameSnake
from apps.core.factories import GameFactory, SnakeFactory
from apps.core.jobs import GameStatus

game_factory = GameFactory()
snake_factory = SnakeFactory()
user_factory = UserFactory()


@mock.patch("apps.core.engine.status")
@mock.patch("apps.core.engine.create")
def test_game_status_job(create_mock, status_mock):
    create_mock.return_value = str(uuid.uuid4())
    game = game_factory.basic()
    game.save()
    snakes = snake_factory.basic(
        n=8, commit=True, profile=user_factory.basic(commit=True).profile
    )

    game.engine_id = str(uuid.uuid4())
    for s in snakes:
        game.snakes.add(s)
        GameSnake.objects.create(game=game, snake=s)
    game.create()
    game_snakes = GameSnake.objects.filter(game_id=game.id)

    status_mock.return_value = {
        "status": "running",
        "turn": 10,
        "snakes": {snake.id: {"death": "starvation"} for snake in game_snakes},
    }

    GameStatus().run()

    game = Game.objects.get(id=game.id)
    assert game.status == "running"
    assert game.turn == 10
