from apps.authentication.factories import UserFactory
from apps.core.forms import SnakeForm
from apps.core.models import Snake

user_factory = UserFactory()


def test_new_snake():
    user = user_factory.basic(commit=True)
    form = SnakeForm(
        user.profile,
        {"name": "DSnek", "url": "https://dsnek.herokuapp.com", "is_public": True},
    )
    form.save()
    user.refresh_from_db()
    snake = user.profile.snakes.get(name="DSnek")
    assert snake.url == "https://dsnek.herokuapp.com"
    assert snake.is_public is True


def test_update_existing_snake():
    user = user_factory.basic(commit=True)
    snake = Snake.objects.create(profile=user.profile, name="DSnek")
    form = SnakeForm(
        user.profile,
        {"name": "DSnek", "url": "https://dsnek.herokuapp.com", "is_public": True},
        instance=snake,
    )

    assert snake.url == ""
    assert snake.is_public is False

    form.save()
    user.refresh_from_db()
    snake = user.profile.snakes.get(name="DSnek")
    assert snake.url == "https://dsnek.herokuapp.com"
    assert snake.is_public is True


def test_new_snake_with_name_collision():
    user = user_factory.basic(commit=True)
    Snake.objects.create(profile=user.profile, name="DSnek")
    form = SnakeForm(
        user.profile,
        {"name": "DSnek", "url": "https://dsnek.herokuapp.com", "is_public": True},
    )
    assert form.is_valid() is False
    assert len(form.errors) == 1


def test_update_snake_with_name_collision():
    user = user_factory.basic(commit=True)
    Snake.objects.create(profile=user.profile, name="DSnek")
    snake = Snake.objects.create(profile=user.profile, name="DSnek1")
    form = SnakeForm(
        user.profile,
        {"name": "DSnek", "url": "https://dsnek.herokuapp.com", "is_public": True},
        instance=snake,
    )
    assert form.is_valid() is False
    assert len(form.errors) == 1
