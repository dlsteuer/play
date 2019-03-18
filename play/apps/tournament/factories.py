from apps.authentication.models import User
from apps.core.models import Profile, Snake
from apps.tournament.models import Team, Tournament, TournamentBracket, TournamentSnake


class TeamFactory:
    def basic(self, user=None):
        team = Team.objects.create(name="test", description="test")
        if user:
            team.team_members.add(user.profile)
        return team


class TournamentFactory:
    def createEmpty(self):
        return Tournament.objects.create(
            name="test", date="2019-01-02", status=Tournament.IN_PROGRESS
        )

    def basic(self, url):

        users = []
        for i in range(0, 40):
            user = User.objects.create(username="user " + str(i))
            users.append(user)
            Profile.objects.create(user=user)

        teams = []
        for i in range(0, 40):
            team = Team.objects.create(
                name="team " + str(i), description="descrption " + str(i)
            )
            teams.append(team)
            team.team_members.add(users[39 - i].profile)

        snakes = []
        for i in range(0, 40):
            snakes.append(
                Snake.objects.create(
                    profile=users[i].profile, name="snake " + str(i), url=url
                )
            )

        tournament = Tournament.objects.create(name="test", date="2019-01-02")
        bracketBeginner = TournamentBracket.objects.create(
            name="Beginner", tournament_id=tournament.id
        )
        bracketIntermediate = TournamentBracket.objects.create(
            name="Intermediate", tournament_id=tournament.id
        )
        bracketAdvanced = TournamentBracket.objects.create(
            name="Advanced", tournament_id=tournament.id
        )

        for i in range(0, 18):
            TournamentSnake.objects.create(
                snake_id=snakes[i].id,
                bracket_id=bracketBeginner.id,
                tournament_id=tournament.id,
            )
        for i in range(18, 32):
            TournamentSnake.objects.create(
                snake_id=snakes[i].id,
                bracket_id=bracketIntermediate.id,
                tournament_id=tournament.id,
            )
        for i in range(32, 40):
            TournamentSnake.objects.create(
                snake_id=snakes[i].id,
                bracket_id=bracketAdvanced.id,
                tournament_id=tournament.id,
            )

        return tournament
