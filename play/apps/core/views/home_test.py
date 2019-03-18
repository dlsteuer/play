from apps.authentication.factories import UserFactory
from apps.core.factories import GameFactory, SnakeFactory
from apps.core.models import GameSnake

game_factory = GameFactory()
snake_factory = SnakeFactory()
user_factory = UserFactory()


def test_home(client):
    engine_id = "a879f127-55c2-4b0c-99c9-bce09c9fc0cf"
    url = "game=" + engine_id

    games = game_factory.basic(
        n=20, engine_id=engine_id, status="complete", turn=200, commit=True
    )
    game = games[0]
    profile = user_factory.basic(commit=True).profile
    GameSnake.objects.create(game=game, snake=snake_factory.basic(profile=profile))
    GameSnake.objects.create(game=game, snake=snake_factory.basic(profile=profile))
    response = client.get("/")
    assert response.status_code == 200
    assert url in response.content.decode("utf-8")
