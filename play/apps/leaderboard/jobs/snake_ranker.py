import logging

import trueskill

from apps.core.models import Game
from apps.leaderboard.models import GameLeaderboard, LeaderboardResult

logger = logging.getLogger(__name__)


class SnakeRanker:
    """ A job that iterates over all unranked leaderboard games and ranks them. """

    def run(self):
        for game_leaderboard in (
            GameLeaderboard.objects.filter(
                ranked=False, game__status=Game.Status.COMPLETE
            )
            .order_by("modified")
            .prefetch_related("game__gamesnake_set__snake")
        ):
            try:
                self.rank(game_leaderboard.game)
            except Exception:
                logger.exception(f"failed to rank game id={game_leaderboard.game_id}")
            finally:
                game_leaderboard.ranked = True
                game_leaderboard.save()

    def rank(self, game):
        logger.info(f"ranking game id={game.id}")
        status = game.engine_status()

        sorted_snakes = sorted(
            status["snakes"].items(),
            key=lambda i: game.turn + 1 if i[1]["death"] == "pending" else i[1]["turn"],
            reverse=True,
        )
        lookup = []
        for s in sorted_snakes:
            gs = game.gamesnake_set.get(id=s[0])
            lookup.append(
                {
                    "rating": (
                        self.create_rating(gs.snake.snakeleaderboard_set.first()),
                    ),
                    "snake": gs.snake,
                }
            )
        ratings = [i["rating"] for i in lookup]

        new_rankings = trueskill.rate(ratings, ranks=get_rankings(sorted_snakes))
        for index, new_rank in enumerate(new_rankings):
            t = lookup[index]
            sl = t["snake"].snakeleaderboard_set.first()
            sl.mu = new_rank[0].mu
            sl.sigma = new_rank[0].sigma
            sl.save()
            LeaderboardResult.objects.create(
                snake=t["snake"].snakeleaderboard_set.first(),
                game=game,
                mu_change=new_rank[0].mu - t["rating"][0].mu,
                sigma_change=new_rank[0].sigma - t["rating"][0].sigma,
            )

    def create_rating(self, leaderboard_snake):
        if leaderboard_snake.mu is None or leaderboard_snake.sigma is None:
            return trueskill.Rating()
        return trueskill.Rating(mu=leaderboard_snake.mu, sigma=leaderboard_snake.sigma)


def get_rankings(sorted_snakes):
    rankings = []
    current_rank = 0
    previous_snake = None
    for snake in sorted_snakes:
        if previous_snake is not None:
            if previous_snake[1]["turn"] != snake[1]["turn"]:
                current_rank += 1
            elif (
                previous_snake[1]["death"] == "pending"
                and snake[1]["death"] != "pending"
            ):
                current_rank += 1
        rankings.append(current_rank)
        previous_snake = snake
    return rankings
