import math

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from apps.core.models import Snake, Game, GameSnake
from apps.tournament.models import Team
from apps.utils.helpers import generate_game_url
from util.fields import ShortUUIDField


class PreviousGameTiedException(ValidationError):
    def __init__(self):
        super().__init__(message="Previous game ended in a tie.")


class SingleSnakePerTeamPerTournamentValidationError(ValidationError):
    def __init__(self):
        super().__init__(message="Only one snake per event per team")


class TournamentClosedValidationError(ValidationError):
    def __init__(self):
        super().__init__(message="Tournament over")


class DesiredGamesReachedValidationError(ValidationError):
    def __init__(self):
        super().__init__(message="No more games should be run for this heat")


class RoundNotCompleteException(ValidationError):
    def __init__(self):
        super().__init__(message="Complete all games before creating next round.")


class TournamentBracketCompleteException(ValidationError):
    def __init__(self):
        super().__init__(
            message="Tournament Bracket is complete, can't create another round."
        )


class Tournament(models.Model):
    LOCKED = "LO"  # Not started, but nobody can register
    HIDDEN = "HI"  # Able to add snakes manually (invite-only)
    REGISTRATION = "RE"  # Publicly viewable and opt-in-able
    IN_PROGRESS = "PR"
    COMPLETE = "JR"
    STATUSES = (
        (LOCKED, "Locked"),
        (HIDDEN, "Hidden"),
        (REGISTRATION, "Registration"),
        (IN_PROGRESS, "In Progress"),
        (COMPLETE, "Complete"),
    )

    id = ShortUUIDField(prefix="trn", max_length=128, primary_key=True)
    casting_uri = models.CharField(default="", max_length=1024)
    status = models.CharField(max_length=2, choices=STATUSES, default=LOCKED)
    name = models.CharField(max_length=256)
    date = models.DateField()
    snakes = models.ManyToManyField(
        Snake, through="TournamentSnake", through_fields=("tournament", "snake")
    )
    engine_url = models.CharField(default=settings.ENGINE_URL, max_length=128)

    @property
    def brackets(self):
        return TournamentBracket.objects.filter(tournament=self)

    @property
    def is_registration_open(self):
        return self.status == self.REGISTRATION

    def __str__(self):
        return f"Tournament {self.name}"


class TournamentBracket(models.Model):
    id = ShortUUIDField(prefix="tbr", max_length=128, primary_key=True)
    name = models.CharField(max_length=256)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    board_width = models.IntegerField(default=11)
    board_height = models.IntegerField(default=11)
    board_food = models.IntegerField(default=2)
    board_max_turns_to_next_food_spawn = models.IntegerField(
        null=True, blank=True, default=15
    )
    snakes = models.ManyToManyField(
        Snake, through="TournamentSnake", through_fields=("bracket", "snake")
    )

    cached_rounds = None

    header_row = ["Round", "Heat", "Team Name", "Team ID", "Team Snake URL"]

    def update_heat_games(self):
        if self.latest_round is not None:
            for heat in self.latest_round.heats:
                for hg in heat.games:
                    if hg.game.engine_id is not None:
                        hg.game.update_from_engine()
                        hg.game.save()

    def create_next_round(self):
        if self.latest_round is not None:
            if self.latest_round.status != "complete":
                raise RoundNotCompleteException
            if (
                self.latest_round.heats.count() == 1
                and len(self.latest_round.snakes) == 2
            ):
                raise TournamentBracketCompleteException

        num = max([r.number for r in self.rounds] + [0]) + 1
        self.cached_rounds = None  # clear out cached data
        return Round.objects.create(number=num, tournament_bracket=self)

    @property
    def rounds(self):
        if self.cached_rounds is None:
            self.cached_rounds = list(
                self.round_set.all()
                .prefetch_related(
                    "heat_set__heatgame_set__game",
                    "heat_set__heatgame_set__game__gamesnake_set",
                    "heat_set__snakeheat_set__snake",
                )
                .order_by("number")
            )
        return self.cached_rounds

    @property
    def latest_round(self):
        if len(self.rounds) == 0:
            return None
        return self.rounds[-1]

    def get_complete_final_round(self):
        if self.latest_round is None:
            return None

        # the final round has exactly one heat
        if self.latest_round.heats.count() != 1:
            return None
        last_heat = self.latest_round.heats.first()

        if len(last_heat.games) != 1:
            return None
        if self.latest_round.status != "complete":
            return None
        if len(last_heat.games[-1].snakes) != 2:
            return None
        return self.latest_round

    @property
    def winners(self):
        last_round = self.get_complete_final_round()
        if last_round is None:
            return False

        first_place_game = last_round.heats[0].games[0]

        # It's a tie!
        if first_place_game.winner is None:
            return []

        # first snake
        first_place = first_place_game.winner

        # second snake
        top_two_snakes = first_place_game.game.game_snakes
        second_place = [snake for snake in top_two_snakes if snake != first_place][0]

        third_place_round = last_round.previous
        if third_place_round is None:
            return [first_place, second_place]

        # third snake
        third_place_game = third_place_round.heats[0].games[0]
        third_place = [
            gs
            for gs in third_place_game.game.game_snakes
            if gs.snake not in [first_place.snake, second_place.snake]
        ][0]

        return [first_place, second_place, third_place]

    @property
    def runner_ups(self):
        winners = self.winners
        if winners is False:
            return False

        round = self.latest_round
        if round is None:
            return []
        while True:
            if len(round.snakes) >= 4:
                break
            if round.previous is None:
                break
            round = round.previous

        final_six_game = round.heats[0].games[0]
        final_six = final_six_game.game.game_snakes
        game_snakes = final_six.exclude(snake_id__in=[w.snake_id for w in winners])
        return game_snakes

    @property
    def snake_count(self):
        return self.snakes.count()

    def game_details(self):
        games = []
        for r in self.rounds:
            for heat in r.heats:
                for hg in heat.games:
                    status = hg.game.status if hg.game is not None else None
                    games.append(
                        {
                            "id": hg.game.id,
                            "url": generate_game_url(hg.game),
                            "status": status,
                            "round": r.number,
                            "heat": heat.number,
                            "heat_game": hg.number,
                        }
                    )
        return games

    def export(self):
        rows = [self.header_row]
        for r in self.rounds:
            for heat in r.heats:
                for snake in heat.snakes:
                    row = [
                        f"Round {r.number}",
                        f"Heat {heat.number}",
                        snake.team.name,
                        snake.team.id,
                        snake.snake.url,
                    ]
                    rows.append(row)
        return rows

    def __str__(self):
        return f"[{self.tournament.name}] {self.name}"

    class Meta:
        app_label = "tournament"


class TournamentSnake(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    snake = models.ForeignKey(Snake, on_delete=models.CASCADE)
    bracket = models.ForeignKey(TournamentBracket, null=True, on_delete=models.SET_NULL)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, null=True)

    @classmethod
    def get_snake_names(cls, tournament):
        tournament_snakes = TournamentSnake.objects.filter(
            tournament=tournament
        ).prefetch_related("team", "bracket", "snake")
        snake_names = {}
        for ts in tournament_snakes:
            snake_names[ts.snake.id] = ts.team.name
        return snake_names

    @classmethod
    def get_snake_descriptions(cls, tournament):
        tournament_snakes = TournamentSnake.objects.filter(
            tournament=tournament
        ).prefetch_related("team", "bracket", "snake")
        snake_names = {}
        for ts in tournament_snakes:
            snake_names[ts.snake.id] = ts.team.description
        return snake_names

    def __str__(self):
        return f"[{self.tournament.name}:{self.bracket.name}] {self.team.name}"

    class Meta:
        app_label = "tournament"


class RoundManager(models.Manager):
    def create(self, *args, **kwargs):
        round = super(RoundManager, self).create(*args, **kwargs)
        max_snakes_per = 8
        num_snakes = len(round.snakes)

        if num_snakes in [4, 5, 6, 7, 8]:
            heat = Heat.objects.create(number=1, round=round, desired_games=3)
            for snake in round.snakes:
                SnakeHeat.objects.create(snake=snake, heat=heat)
            return round

        elif num_snakes == 3:
            heat = Heat.objects.create(number=1, round=round, desired_games=2)
            for snake in round.snakes:
                SnakeHeat.objects.create(snake=snake, heat=heat)
            return round

        elif num_snakes == 2:
            heat = Heat.objects.create(number=1, round=round, desired_games=1)
            for snake in round.snakes:
                SnakeHeat.objects.create(snake=snake, heat=heat)
            return round

        # create heats
        num_heats = int(math.ceil(num_snakes / max_snakes_per))
        if 12 <= num_snakes <= 24:
            num_heats = 3
        if num_snakes > 24 and num_heats == 4:
            num_heats = 6
        heats = [
            Heat.objects.create(number=i + 1, round=round, desired_games=2)
            for i in range(0, num_heats)
        ]

        i = 0
        for snake in round.snakes:
            SnakeHeat.objects.create(snake=snake, heat=heats[i % num_heats])
            i += 1

        return round


class Round(models.Model):
    NAME_FINAL_6 = "The Final 6"
    NAME_FINAL_3 = "The Final 3"
    NAME_FINAL_2 = "The Final 2"

    id = ShortUUIDField(prefix="rnd", max_length=128, primary_key=True)
    number = models.IntegerField(default=1)
    tournament_bracket = models.ForeignKey(TournamentBracket, on_delete=models.CASCADE)

    objects = RoundManager()

    @property
    def previous(self):
        try:
            return Round.objects.get(
                number=self.number - 1, tournament_bracket=self.tournament_bracket
            )
        except Round.DoesNotExist:
            return None

    @property
    def snakes(self):
        if self.number == 1:
            return [s for s in self.tournament_bracket.snakes.all()]
        return [s.snake for s in self.previous.winners]

    @property
    def _heat_count(self):
        if not hasattr(self, "__heat_count"):
            self.__heat_count = self.heats.count()
        return self.__heat_count

    @property
    def name(self):
        if self._heat_count > 1:
            return f"Round {self.number}"

        num_snakes = self.snake_count
        if num_snakes == 2:
            return self.NAME_FINAL_2

        if num_snakes == 3:
            return self.NAME_FINAL_3

        return self.NAME_FINAL_6

    @property
    def snake_count(self):
        return len(self.snakes)

    @property
    def winners(self):
        winners = []
        for heat in self.heats:
            winners += heat.winners
        return winners

    @property
    def heats(self):
        return (
            self.heat_set.all()
            .order_by("number")
            .prefetch_related("heatgame_set", "snakeheat_set")
        )

    @property
    def status(self):
        for heat in self.heats:
            if heat.status != "complete":
                return heat.status
        return "complete"

    def __str__(self):
        return f"[{self.tournament_bracket.tournament.name}:{self.tournament_bracket.name}] {self.name}"

    class Meta:
        app_label = "tournament"
        unique_together = ("number", "tournament_bracket")


class Heat(models.Model):
    id = ShortUUIDField(prefix="hea", max_length=128, primary_key=True)
    number = models.IntegerField(default=1)
    round = models.ForeignKey(Round, on_delete=models.CASCADE)
    desired_games = models.IntegerField(default=2)

    cached_heatgames = None

    def __str__(self):
        return f"[{self.round.tournament_bracket.tournament.name}:{self.round.tournament_bracket.name}:{self.round.name}] Heat {self.number}"

    @property
    def snakes(self):
        return self.snakeheat_set.all().prefetch_related(
            "snake", "heat", "heat__heatgame_set"
        )

    @property
    def ordered_snakes(self):
        snakes = list(self.snakes)
        ordered_snakes = []
        for s in snakes:
            if s.first:
                ordered_snakes.append(s)
                snakes.remove(s)
                break
        for s in snakes:
            if s.second:
                ordered_snakes.append(s)
                snakes.remove(s)
                break
        for s in snakes:
            if s.third:
                ordered_snakes.append(s)
                snakes.remove(s)
                break
        for s in snakes:
            ordered_snakes.append(s)
        return ordered_snakes

    @property
    def games(self):
        if self.cached_heatgames is None:
            self.cached_heatgames = list(self.heatgame_set.all().order_by("number"))
        return self.cached_heatgames

    @property
    def latest_game(self):
        if len(self.games) == 0:
            return None
        return self.games[0]

    @property
    def winners(self):
        winners = []
        for game in self.games:
            if game.winner is not None:
                winners.append(game.winner)

        return winners

    @property
    def status(self):
        if len(self.games) < self.desired_games:
            return "running"

        for hg in self.games:
            if hg.game.status is not Game.Status.COMPLETE:
                return hg.game.status
        return "complete"

    def create_next_game(self):
        if len(self.games) >= self.desired_games:
            raise DesiredGamesReachedValidationError()

        n = len(self.games) + 1

        if (
            self.latest_game is not None
            and self.latest_game.game.status != Game.Status.COMPLETE
        ):
            raise Exception("can't create next game")
        hg = HeatGame.objects.create(heat=self, number=n)
        return hg

    class Meta:
        app_label = "tournament"


class HeatGameManager(models.Manager):
    def create(self, *args, **kwargs):
        heat = kwargs.get("heat")
        previous_game = heat.latest_game
        skip = [w.snake.id for w in heat.winners]
        if previous_game is not None:
            if previous_game.winner is None:
                raise PreviousGameTiedException()
            skip.append(previous_game.winner.snake.id)
            next_snakes = [
                sh.snake for sh in previous_game.snakes if sh.snake.id not in skip
            ]
        else:
            next_snakes = [sh.snake for sh in heat.snakes]

        max_turns = 15
        if heat.round.tournament_bracket.board_max_turns_to_next_food_spawn is not None:
            max_turns = heat.round.tournament_bracket.board_max_turns_to_next_food_spawn

        game = Game(
            width=heat.round.tournament_bracket.board_width,
            height=heat.round.tournament_bracket.board_height,
            max_turns_to_next_food_spawn=max_turns,
            engine_url=heat.round.tournament_bracket.tournament.engine_url,
        )
        game.save()

        snake_ids = [snake.id for snake in next_snakes]
        snakes = (
            TournamentSnake.objects.filter(
                snake__id__in=snake_ids, bracket=heat.round.tournament_bracket
            )
            .prefetch_related("snake")
            .prefetch_related("team")
        )
        for ts in snakes:
            game.snakes.add(ts.snake)
            GameSnake.objects.create(snake=ts.snake, game=game, name=ts.team.name)
        game.save()
        game.create()

        return super(HeatGameManager, self).create(*args, **kwargs, game=game)


class HeatGame(models.Model):
    UNWATCHED = "UW"
    WATCHING = "W"
    WATCHED = "WD"
    STATUSES = (
        (UNWATCHED, "Not Casted Yet"),
        (WATCHING, "Casting"),
        (WATCHED, "Casted"),
    )

    id = ShortUUIDField(prefix="hga", max_length=128, primary_key=True)
    status = models.CharField(max_length=2, choices=STATUSES, default=UNWATCHED)
    number = models.IntegerField(default=1)
    heat = models.ForeignKey(Heat, on_delete=models.CASCADE)
    game = models.ForeignKey("core.Game", on_delete=models.DO_NOTHING)

    objects = HeatGameManager()

    @property
    def snakes(self):
        if self.previous is None:
            return self.heat.snakes
        return [
            s for s in self.previous.snakes if s.snake != self.previous.winner.snake
        ]

    @property
    def winner(self):
        if not hasattr(self, "_winner") or self._winner is None:
            self._winner = self.game.winner()
        return self._winner

    @property
    def human_readable_status(self):
        for (short, name) in self.STATUSES:
            if self.status == short:
                return name

    @property
    def previous(self):
        if self.number == 1:
            return None
        return HeatGame.objects.get(number=self.number - 1, heat=self.heat)


class SnakeHeat(models.Model):
    heat = models.ForeignKey(Heat, on_delete=models.CASCADE)
    snake = models.ForeignKey(Snake, on_delete=models.CASCADE)

    tournament_snake = None

    @property
    def team(self):
        if self.tournament_snake is None:
            self.tournament_snake = TournamentSnake.objects.filter(
                snake_id=self.snake.id
            ).prefetch_related("team")[0]
        return self.tournament_snake.team

    @property
    def first(self):
        if len(self.heat.games) == 0:
            return False
        if self.heat.games[0].winner is None:
            return False
        return self.heat.games[0].winner.name == self.team.name

    @property
    def second(self):
        if len(self.heat.games) <= 1:
            return False
        if self.heat.games[1].winner is None:
            return False
        return self.heat.games[1].winner.name == self.team.name

    @property
    def third(self):
        if len(self.heat.games) <= 2:
            return False
        if self.heat.games[2].winner is None:
            return False
        return self.heat.games[2].winner.name == self.team.name

    class Meta:
        app_label = "tournament"
        unique_together = ("heat", "snake")
