import mock
import uuid
import random

from apps.leaderboard.jobs.snake_ranker import get_rankings
from apps.leaderboard.models import SnakeLeaderboard, LeaderboardResult, GameLeaderboard
from apps.leaderboard.jobs import MatchStarter, SnakeRanker
from apps.authentication.factories import UserFactory
from apps.core.factories import SnakeFactory
from apps.core.models import GameSnake, Game

user_factory = UserFactory()
snake_factory = SnakeFactory()


def test_create_rankings_single_winner():
    status = {
        "status": "complete",
        "turn": 30,
        "snakes": {
            "gs_pjpqBg9c83M3wtqHSqKqBDSV": {"death": "wall-collision", "turn": 2},
            "gs_b6Hty73b8PfGY4GvppjCxCQf": {"death": "head-collision", "turn": 27},
            "gs_BFjTqtbY3PwCtqyBGd8j74YD": {"death": "wall-collision", "turn": 30},
            "gs_mVYdM8CMmHbv3YRxdFKBVv6D": {"death": "wall-collision", "turn": 2},
            "gs_Sxgdq6TTKqpxHxHDjrXHpkSd": {"death": "wall-collision", "turn": 29},
            "gs_TfK3wyHYMjb6rYFjd7RJTy9f": {"death": "pending", "turn": 30},
            "gs_CRrVQb6jK6SrfJYXRkCb9b68": {"death": "snake-collision", "turn": 9},
        },
    }
    sorted_snakes = sorted(
        status["snakes"].items(),
        key=lambda i: 31 if i[1]["death"] == "pending" else i[1]["turn"],
        reverse=True,
    )
    print(sorted_snakes)
    rankings = get_rankings(sorted_snakes)
    assert [0, 1, 2, 3, 4, 5, 5] == rankings


def test_create_rankings_tie():
    status = {
        "status": "complete",
        "turn": 30,
        "snakes": {
            "gs_pjpqBg9c83M3wtqHSqKqBDSV": {"death": "wall-collision", "turn": 2},
            "gs_b6Hty73b8PfGY4GvppjCxCQf": {"death": "head-collision", "turn": 27},
            "gs_BFjTqtbY3PwCtqyBGd8j74YD": {"death": "pending", "turn": 30},
            "gs_mVYdM8CMmHbv3YRxdFKBVv6D": {"death": "wall-collision", "turn": 2},
            "gs_Sxgdq6TTKqpxHxHDjrXHpkSd": {"death": "wall-collision", "turn": 29},
            "gs_TfK3wyHYMjb6rYFjd7RJTy9f": {"death": "pending", "turn": 30},
            "gs_CRrVQb6jK6SrfJYXRkCb9b68": {"death": "snake-collision", "turn": 9},
        },
    }
    sorted_snakes = sorted(
        status["snakes"].items(),
        key=lambda i: 31 if i[1]["death"] == "pending" else i[1]["turn"],
        reverse=True,
    )
    print(sorted_snakes)
    rankings = get_rankings(sorted_snakes)
    assert [0, 0, 1, 2, 3, 4, 4] == rankings


@mock.patch("apps.core.engine.status")
@mock.patch("apps.core.engine.create")
@mock.patch("apps.core.engine.run")
def test_update_leaderboard_game(run_mock, create_mock, status_mock):

    create_mock.return_value = str(uuid.uuid4())

    snakes = snake_factory.basic(
        n=10, commit=True, profile=user_factory.basic(commit=True).profile
    )
    for s in snakes:
        s.save()
        SnakeLeaderboard.objects.get_or_create(snake=s)

    MatchStarter().run()

    game_snakes = GameSnake.objects.all()

    snakes_dict = {
        snake.id: {"death": "starvation", "turn": random.randint(1, 100)}
        for snake in game_snakes
    }
    snakes_dict[game_snakes[0].id]["death"] = "pending"
    snakes_dict[game_snakes[0].id]["turn"] = 125
    snakes_dict[game_snakes[1].id]["turn"] = 125

    status_mock.return_value = {
        "status": Game.Status.COMPLETE,
        "turn": 125,
        "snakes": snakes_dict,
    }

    SnakeRanker().run()

    # Game is not complete, no ranking should happen
    gl = GameLeaderboard.objects.first()
    for gs in gl.game.gamesnake_set.all():
        lb = gs.snake.snakeleaderboard_set.first()
        assert lb.mu is None
        assert lb.sigma is None

    for game in Game.objects.all():
        game.update_from_engine()

    SnakeRanker().run()

    # Game is now complete, so let's rank
    gl = GameLeaderboard.objects.first()
    for gs in gl.game.gamesnake_set.all():
        lb = gs.snake.snakeleaderboard_set.first()
        assert lb.mu is not None
        assert lb.sigma is not None

        result = LeaderboardResult.objects.get(snake=lb)
        assert result is not None
        assert result.mu_change is not None
        assert result.sigma_change is not None

    assert gl.game.leaderboardresult_set.count() == gl.game.gamesnake_set.count()

    for gl in GameLeaderboard.objects.all():
        assert gl.ranked
    assert GameLeaderboard.objects.all().count() > 0
