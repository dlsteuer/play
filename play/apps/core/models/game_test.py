import mock
import uuid

from apps.authentication.factories import UserFactory
from apps.core.models import GameSnake
from apps.core.factories import GameFactory, SnakeFactory

snake_factory = SnakeFactory()
game_factory = GameFactory()
user_factory = UserFactory()


@mock.patch("apps.core.engine.create")
def test_game_engine_configuration(create_mock):
    create_mock.return_value = str(uuid.uuid4())
    game = game_factory.basic()
    game.save()

    snakes = snake_factory.basic(
        n=8, commit=True, profile=user_factory.basic(commit=True).profile
    )
    for snake in snakes:
        game.snakes.add(snake)
        GameSnake.objects.create(snake=snake, game=game)
    game.create()

    config = game.config()
    assert config["height"] == 20
    assert config["width"] == 20
    assert config["food"] == len(snakes)
    assert config["snakes"][0]["id"] is not None
    assert config["snakes"][0]["name"] == "test / test"
    assert len(config["snakes"]) == 8


@mock.patch("apps.core.engine.run")
@mock.patch("apps.core.engine.create")
def test_game_engine_call(create_mock, run_mock):
    create_mock.return_value = str(uuid.uuid4())

    game = game_factory.basic()
    game.save()

    snakes = snake_factory.basic(
        n=8, commit=True, profile=user_factory.basic(commit=True).profile
    )
    for snake in snakes:
        game.snakes.add(snake)
        GameSnake.objects.create(snake=snake, game=game)

    assert game.engine_id is None

    game.create()
    assert game.engine_id is not None

    game.run()
    assert len(run_mock.call_args_list) == 1
    assert game.engine_id is not None


@mock.patch("apps.core.engine.status")
@mock.patch("apps.core.engine.create")
def test_game_engine_update(create_mock, status_mock):
    create_mock.return_value = str(uuid.uuid4())
    game = game_factory.basic()
    game.save()
    snakes = snake_factory.basic(
        n=8, commit=True, profile=user_factory.basic(commit=True).profile
    )

    game.engine_id = str(uuid.uuid4())
    for snake in snakes:
        game.snakes.add(snake)
        GameSnake.objects.create(snake=snake, game=game)

    game.create()
    game_snakes = GameSnake.objects.filter(game_id=game.id)

    status_mock.return_value = {
        "status": "running",
        "turn": 10,
        "snakes": {snake.id: {"death": "starvation"} for snake in game_snakes},
    }

    game.update_from_engine()
    assert len(status_mock.call_args_list) == 1
    assert game.status == "running"
    assert game.turn == 10


def test_game_create_game_snake_name_overrides_snake_name():
    game = game_factory.basic()
    game.save()
    snakes = snake_factory.basic(
        n=2, commit=True, profile=user_factory.basic(commit=True).profile
    )

    game.snakes.add(snakes[0])
    GameSnake.objects.create(snake=snakes[0], game=game)
    game.snakes.add(snakes[1])
    GameSnake.objects.create(snake=snakes[0], game=game, name="Not A Test")

    config = game.config()
    found = False
    for s in config["snakes"]:
        if s["name"] == "Not A Test":
            found = True

    assert found is True
