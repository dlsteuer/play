import json

import mock
import pytest
from apps.core.factories import GameFactory, SnakeFactory
from apps.authentication.factories import UserFactory

user_factory = UserFactory()
snake_factory = SnakeFactory()
game_factory = GameFactory()


@pytest.fixture
def user(client):
    user = user_factory.login_as(client)
    return user


def test_new(user, client):
    response = client.get("/g/new/")
    assert response.status_code == 200


@mock.patch("apps.core.engine.run")
@mock.patch("apps.core.engine.create")
def test_create(create_mock, run_mock, user, client):
    create_mock.return_value = "a879f127-55c2-4b0c-99c9-bce09c9fc0cf"

    snake1 = snake_factory.basic(n=1, commit=True, profile=user.profile)
    snake2 = snake_factory.basic(n=1, commit=True, profile=user.profile)

    response = client.post(
        "/g/new/", {"board_size": "medium", "snakes": f"{snake1.id},{snake2.id}"}
    )
    assert response.status_code == 302
    assert len(create_mock.call_args_list) == 1
    assert len(run_mock.call_args_list) == 1


def test_show(user, client):
    engine_id = "a879f127-55c2-4b0c-99c9-bce09c9fc0cf"
    url = "game=" + engine_id

    game_factory.basic(engine_id=engine_id, commit=True)

    response = client.get(f"/g/{engine_id}/")
    assert response.status_code == 200
    assert url in response.content.decode("utf-8")


def test_snake_autocomplete(user, client):
    snake = snake_factory.basic(n=1, profile=user.profile)
    snake.name = "snaker"
    snake.save()
    response = client.get(f"/g/snake-autocomplete/?q={user.username}")
    j = json.loads(response.content)
    assert len(j) == 1
    assert j[0]["text"] == f"{user.username} / {snake.name}"
    response = client.get(f"/g/snake-autocomplete/?q={snake.name}")
    j = json.loads(response.content)
    assert len(j) == 1
    assert j[0]["text"] == f"{user.username} / {snake.name}"
