import random
import logging

from django.db.models import Q
from django.db import transaction

from apps.leaderboard.models import SnakeLeaderboard, GameLeaderboard
from apps.core.models import Game, Snake, GameSnake

logger = logging.getLogger(__name__)


class MatchStarter:
    def chunks(self, l, n):
        """Yield successive n-sized chunks from l."""
        for i in range(0, len(l), n):
            yield l[i : i + n]  # noqa: E203

    def matches(self):
        """ Select matches to run. A random mix of snakes. """
        snake_ids = list(
            SnakeLeaderboard.objects.all()
            .order_by("-mu")
            .values_list("snake_id", flat=True)
        )

        current_leaderboard_games = list(
            GameLeaderboard.objects.filter(
                Q(game__status=Game.Status.RUNNING)
                | Q(game__status=Game.Status.PENDING)
                | Q(game__status=Game.Status.CREATED)
            )
        )
        for lb_game in current_leaderboard_games:
            for gs in lb_game.game.game_snakes.all():
                if gs.snake.id in snake_ids:
                    snake_ids.remove(gs.snake.id)
        matches = []
        while True:
            match_size = random.randint(0, 3) + 5
            logger.info(f"Creating matches of size: {match_size}")
            if match_size > len(snake_ids):
                break

            potential = snake_ids[: match_size + 5]
            random.shuffle(potential)
            matches.append(potential[:match_size])
            for snake_id in potential:
                snake_ids.remove(snake_id)

        return matches

    @transaction.atomic
    def start_game(self, snake_ids):
        """ Start a game given a tuple of snake id's. Returning a game id. """
        if len(snake_ids) == 1:
            return

        game = Game(width=11, height=11, max_turns_to_next_food_spawn=12)
        game.save()

        logger.info(f"starting game id={game.id}")

        for s in Snake.objects.filter(id__in=snake_ids):
            game.snakes.add(s)
            GameSnake.objects.create(snake=s, game=game)

        game.save()
        game.create()
        game.run()
        GameLeaderboard(game=game).save()

    def run(self):
        n = 0
        matches = self.matches()
        print("matches found", len(matches))
        for match in matches:
            self.start_game(match)
            n += 1
        return n
