from apps.authentication.factories import UserFactory
from apps.tournament.factories import TeamFactory

user_factory = UserFactory()
team_factory = TeamFactory()


def test_new(client):
    user = user_factory.login_as(client)
    team_factory.basic(user=user)

    response = client.get("/team/members/new/")
    # assert response.status_code == 200
    # Note: we've temporarily disabled the team member creation endpoint
    assert response.status_code == 404


def test_create(client):
    # user_new = user_factory.basic("test2@test.com", commit=True)

    # user = user_factory.login_as(client)
    # team = team_factory.basic(user=user)

    response = client.post("/team/members/new/", {"username": "test2"})
    # assert response.status_code == 302
    # assert TeamMember.objects.get(user=user_new, team=team) is not None
    # Note: we've temporarily disabled the team member creation endpoint
    assert response.status_code == 404


def test_delete(client):
    user = user_factory.login_as(client)
    team = team_factory.basic(user=user)

    user_new = user_factory.basic("test2@test.com", commit=True)
    team.team_members.add(user_new.profile)

    response = client.post(f"/team/members/{user_new.id}/", {"_method": "DELETE"})
    # assert response.status_code == 302
    # assert TeamMember.objects.filter(user=user_new, team=team).first() is None
    # Note: we've temporarily disabled the team member delete endpoint
    assert response.status_code == 404
