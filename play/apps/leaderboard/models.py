from django.db import models

from apps.core.models import Game, Snake
from util.models import BaseModel
from util.fields import ShortUUIDField


class GameLeaderboard(BaseModel):
    """ Tracks a game from the leaderboard perspective. """

    game = models.OneToOneField(Game, null=True, blank=True, on_delete=models.SET_NULL)
    ranked = models.BooleanField(default=False)


class SnakeLeaderboard(BaseModel):
    """ Tracks a snakes involvement in the leaderboard. """

    def __init__(self, *args, **kwargs):
        self._rank = False
        super().__init__(*args, **kwargs)

    id = ShortUUIDField(prefix="slb", max_length=128, primary_key=True)
    snake = models.ForeignKey(Snake, null=True, on_delete=models.CASCADE)
    mu = models.FloatField(null=True)
    sigma = models.FloatField(null=True)

    @property
    def rank(self):
        return self.mu or 25

    @classmethod
    def ranked(cls):
        snakes = list(SnakeLeaderboard.objects.all())
        return sorted(snakes, key=lambda s: s.rank, reverse=True)

    def __str__(self):
        return f"{self.snake.name}"

    class Meta:
        app_label = "leaderboard"


class LeaderboardResult(BaseModel):
    snake = models.ForeignKey(SnakeLeaderboard, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    mu_change = models.FloatField()
    sigma_change = models.FloatField()
