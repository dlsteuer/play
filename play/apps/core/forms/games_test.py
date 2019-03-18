import pytest
from apps.authentication.factories import UserFactory
from apps.core.forms import GameForm
from apps.core.factories import SnakeFactory
from apps.core.models import Game, Snake


snake_factory = SnakeFactory()
user_factory = UserFactory()


def test_save():
    user = user_factory.basic(commit=True)
    snake = snake_factory.basic(n=1, commit=True, profile=user.profile)

    form = GameForm(
        {"width": 10, "height": 10, "board_size": "custom", "snakes": snake.id}
    )

    assert form.is_valid()
    assert isinstance(form.save(user), Game)


def test_hidden_snake():
    user = user_factory.basic(commit=True)
    snake = snake_factory.basic(n=1, commit=True, profile=user.profile)

    form = GameForm(
        {"width": 10, "height": 10, "board_size": "custom", "snakes": snake.id}
    )

    assert form.is_valid()
    with pytest.raises(Snake.DoesNotExist):
        isinstance(
            form.save(user_factory.basic(email="other@test.com", commit=True)), Game
        )
