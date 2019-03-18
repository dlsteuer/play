from apps.authentication.factories import UserFactory
from apps.core.models import Snake

user_factory = UserFactory()


def test_get(client):
    user = user_factory.login_as(client)
    response = client.get(f"/u/{user.username}/")
    assert response.status_code == 200


def test_get_case_insensitive(client):
    user = user_factory.login_as(client)
    response = client.get(f"/u/{user.username.upper()}/")
    assert response.status_code == 302
    assert response.url == f"/u/{user.username}/"


def test_snakes_are_returned_in_response(client):
    user = user_factory.login_as(client)
    Snake.objects.create(profile=user.profile, name="My Snake")
    response = client.get(f"/u/{user.username}/")

    assert response.context[-1]["profile"].user.profile.snakes[0].name == "My Snake"
