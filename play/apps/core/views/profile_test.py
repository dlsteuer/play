from apps.core.models import Profile
from apps.authentication.factories import UserFactory

user_factory = UserFactory()


def test_edit(client):
    user_factory.login_as(client)
    response = client.get("/settings/")
    assert response.status_code == 200


def test_update(client):
    user = user_factory.login_as(client)
    response = client.post("/settings/", {"email": "my-new-email", "_method": "PUT"})
    assert response.status_code == 302
    assert Profile.objects.get(user=user).email == "my-new-email"


def test_update_no_email(client):
    user_factory.login_as(client)
    response = client.post("/settings/", {"email": "", "_method": "PUT"})
    assert response.status_code == 400


def test_delete(client):
    user_factory.login_as(client)
    response = client.delete("/settings/")
    assert response.status_code == 302


def test_delete_no_profile(client):
    user_factory.login_as(client)
    response = client.delete("/settings/")
    assert response.status_code == 302
