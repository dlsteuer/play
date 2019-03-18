from django.db import models

from apps.core.models import Snake, Profile
from util.fields import ShortUUIDField


class Team(models.Model):
    id = ShortUUIDField(prefix="tem", max_length=128, primary_key=True)
    name = models.CharField(max_length=128)
    description = models.TextField(verbose_name="Back Story")
    can_register_in_tournaments = models.BooleanField(default=False)
    team_members = models.ManyToManyField(Profile)

    @property
    def snakes(self):
        return [s for s in Snake.objects.filter(profile__in=self.profiles)]

    @property
    def profiles(self):
        return [profile for profile in self.team_members.all()]

    @property
    def tournament_snakes(self):
        from apps.tournament.models import TournamentSnake

        return TournamentSnake.objects.filter(snake__in=self.snakes)

    @property
    def available_tournaments(self):
        from apps.tournament.models import Tournament

        return Tournament.objects.filter(status=Tournament.REGISTRATION).exclude(
            id__in=[ts.tournament.id for ts in self.tournament_snakes]
        )

    def __str__(self):
        return self.name

    class Meta:
        app_label = "tournament"
