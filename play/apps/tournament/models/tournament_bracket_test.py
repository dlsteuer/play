import datetime
import uuid

import pytest
from mock import mock

from apps.authentication.models import User
from apps.core.models import Profile, Snake, GameSnake
from apps.tournament.models import (
    TournamentBracket,
    Team,
    Round,
    TournamentSnake,
    Tournament,
    RoundNotCompleteException,
)


def _arrange_tournament(name, num_snakes=8):
    tg = Tournament.objects.create(
        name="test tournament",
        date=datetime.datetime.now(),
        status=Tournament.REGISTRATION,
    )
    t = TournamentBracket.objects.create(name=name, tournament=tg)
    for i in range(1, num_snakes + 1):
        user = User.objects.create(username=f"user_{i}")
        profile = Profile.objects.create(user=user)
        snake = Snake.objects.create(
            name=f"Snake {i}", id=f"snk_{i}", profile=user.profile
        )
        team = Team.objects.create(name=f"Test Team {i}", id=f"tem_{i}")
        team.team_members.add(profile)
        TournamentSnake.objects.create(tournament=tg, bracket=t, snake=snake, team=team)
    return t


def _mark_winner(game):
    game.status = game.Status.COMPLETE
    game.save()

    marked_winner = False
    # Marks all snakes dead except the first one
    i = 0
    for gs in GameSnake.objects.filter(game=game).order_by("snake__id"):
        if not marked_winner:
            marked_winner = True
            continue
        gs.death = "snake-collision"
        gs.turns = i
        gs.save()
        i += 1


def _complete_games_in_round(r):
    for heat in r.heats:
        while heat.status != "complete":
            g1 = heat.create_next_game()
            _mark_winner(g1.game)
            heat.cached_heatgames = None


@pytest.mark.skip("something weird in here with how we access django objects")
def test_unable_to_create_next_round_until_all_heats_are_complete():
    bracket = _arrange_tournament("2 rounds", 24)
    print("create first round")
    bracket.create_next_round()

    with pytest.raises(RoundNotCompleteException):
        bracket.create_next_round()

    game = bracket.rounds[0].heats[0].create_next_game()
    _mark_winner(game.game)

    game = bracket.rounds[0].heats[0].create_next_game()
    _mark_winner(game.game)

    with pytest.raises(RoundNotCompleteException):
        bracket.create_next_round()

    game = bracket.rounds[0].heats[1].create_next_game()
    _mark_winner(game.game)
    game = bracket.rounds[0].heats[1].create_next_game()
    _mark_winner(game.game)
    game = bracket.rounds[0].heats[2].create_next_game()
    _mark_winner(game.game)
    game = bracket.rounds[0].heats[2].create_next_game()
    _mark_winner(game.game)

    # this should not throw an exception now that all games have been run
    bracket.create_next_round()


def test_create_next_round_partial_single_heat():
    bracket = _arrange_tournament("single heat", 5)
    bracket.create_next_round()

    rows = bracket.export()

    expected_rows = [
        ["Round", "Heat", "Team Name", "Team ID", "Team Snake URL"],
        ["Round 1", "Heat 1", "Test Team 1", "tem_1", ""],
        ["Round 1", "Heat 1", "Test Team 2", "tem_2", ""],
        ["Round 1", "Heat 1", "Test Team 3", "tem_3", ""],
        ["Round 1", "Heat 1", "Test Team 4", "tem_4", ""],
        ["Round 1", "Heat 1", "Test Team 5", "tem_5", ""],
    ]
    assert bracket.game_details() == []
    assert rows == expected_rows


@mock.patch("apps.core.models.Game.update_from_engine")
@mock.patch("apps.core.engine.create")
def test_bracket_with_2_snakes(create_mock, update_mock):
    create_mock.return_value = str(uuid.uuid4())
    bracket = _arrange_tournament("single heat", 2)

    round1 = bracket.create_next_round()
    assert bracket.winners is False
    _complete_games_in_round(round1)
    bracket.cached_rounds = None

    assert round1.status == "complete"
    assert round1.heats[0].status == "complete"
    assert round1.name == Round.NAME_FINAL_2
    assert len(bracket.winners) == 2
    assert [gs.snake for gs in bracket.winners] == [
        Snake.objects.get(name="Snake 1"),
        Snake.objects.get(name="Snake 2"),
    ]
    assert len(bracket.runner_ups) == 0


@mock.patch("apps.core.models.Game.update_from_engine")
@mock.patch("apps.core.engine.create")
def test_bracket_with_3_snakes(create_mock, update_mock):
    create_mock.return_value = str(uuid.uuid4())
    bracket = _arrange_tournament("single heat", 3)
    round1 = bracket.create_next_round()
    _complete_games_in_round(round1)
    round2 = bracket.create_next_round()
    _complete_games_in_round(round2)

    assert round1.status == "complete"
    assert round1.heats[0].status == "complete"
    assert round1.name == Round.NAME_FINAL_3
    assert round2.name == Round.NAME_FINAL_2
    assert [gs.snake for gs in bracket.winners] == [
        Snake.objects.get(name="Snake 1"),
        Snake.objects.get(name="Snake 2"),
        Snake.objects.get(name="Snake 3"),
    ]
    assert len(bracket.runner_ups) == 0


@mock.patch("apps.core.models.Game.update_from_engine")
@mock.patch("apps.core.engine.create")
def test_bracket_with_4_snakes(create_mock, update_mock):
    create_mock.return_value = str(uuid.uuid4())
    bracket = _arrange_tournament("single heat", 4)

    round1 = bracket.create_next_round()
    _complete_games_in_round(round1)
    round2 = bracket.create_next_round()
    _complete_games_in_round(round2)
    round3 = bracket.create_next_round()
    _complete_games_in_round(round3)

    assert round1.status == "complete"
    assert round1.heats[0].status == "complete"
    assert round1.name == Round.NAME_FINAL_6
    assert round2.name == Round.NAME_FINAL_3
    assert round3.name == Round.NAME_FINAL_2
    assert len(bracket.winners) == 3
    assert [gs.snake for gs in bracket.winners] == [
        Snake.objects.get(name="Snake 1"),
        Snake.objects.get(name="Snake 2"),
        Snake.objects.get(name="Snake 3"),
    ]
    assert [gs.snake for gs in bracket.runner_ups] == [
        Snake.objects.get(name="Snake 4")
    ]


@mock.patch("apps.core.models.Game.update_from_engine")
@mock.patch("apps.core.engine.create")
def test_bracket_with_8_snakes(create_mock, update_mock):
    create_mock.return_value = str(uuid.uuid4())
    bracket = _arrange_tournament("single heat", 8)
    # Round1: 4 (2 games), 4 (2 games) -> 4 winners
    # Round2: 4 (3 games) -> 3 winners
    # Round3: 3 (2 games) -> 2 winners
    # Round4: 2 (1 game) -> 1 winner

    round1 = bracket.create_next_round()
    _complete_games_in_round(round1)
    round2 = bracket.create_next_round()
    _complete_games_in_round(round2)
    round3 = bracket.create_next_round()
    _complete_games_in_round(round3)

    assert round1.status == "complete"
    assert round1.heats[0].status == "complete"
    assert len(bracket.winners) == 3
    assert [gs.snake for gs in bracket.winners] == [
        Snake.objects.get(name="Snake 1"),
        Snake.objects.get(name="Snake 2"),
        Snake.objects.get(name="Snake 3"),
    ]
    assert [gs.snake for gs in bracket.runner_ups] == [
        Snake.objects.get(name="Snake 4"),
        Snake.objects.get(name="Snake 5"),
        Snake.objects.get(name="Snake 6"),
        Snake.objects.get(name="Snake 7"),
        Snake.objects.get(name="Snake 8"),
    ]


@mock.patch("apps.core.models.Game.update_from_engine")
@mock.patch("apps.core.engine.create")
def test_bracket_with_9_snakes(create_mock, update_mock):
    create_mock.return_value = str(uuid.uuid4())
    bracket = _arrange_tournament("single heat", 9)

    round1 = bracket.create_next_round()
    _complete_games_in_round(round1)
    round2 = bracket.create_next_round()
    _complete_games_in_round(round2)
    round3 = bracket.create_next_round()
    _complete_games_in_round(round3)
    round4 = bracket.create_next_round()
    _complete_games_in_round(round4)

    assert round1.status == "complete"
    assert round1.heats[0].status == "complete"
    assert round1.heats[1].status == "complete"
    assert round2.status == "complete"
    assert round2.heats[0].status == "complete"
    assert len(bracket.winners) == 3
    assert [gs.snake for gs in bracket.winners] == [
        Snake.objects.get(name="Snake 1"),
        Snake.objects.get(name="Snake 2"),
        Snake.objects.get(name="Snake 3"),
    ]
    assert [gs.snake for gs in bracket.runner_ups] == [
        Snake.objects.get(name="Snake 4")
    ]


@mock.patch("apps.core.models.Game.update_from_engine")
@mock.patch("apps.core.engine.create")
def test_bracket_with_24_snakes(create_mock, update_mock):
    create_mock.return_value = str(uuid.uuid4())
    bracket = _arrange_tournament("single heat", 24)

    round1 = bracket.create_next_round()
    _complete_games_in_round(round1)
    round2 = bracket.create_next_round()
    _complete_games_in_round(round2)
    round3 = bracket.create_next_round()
    _complete_games_in_round(round3)
    round4 = bracket.create_next_round()
    _complete_games_in_round(round4)

    assert round1.status == "complete"
    assert round2.status == "complete"
    assert len(bracket.winners) == 3
    assert [gs.snake for gs in bracket.winners] == [
        Snake.objects.get(name="Snake 1"),
        Snake.objects.get(name="Snake 10"),
        Snake.objects.get(name="Snake 11"),
    ]
    assert [gs.snake for gs in bracket.runner_ups] == [
        Snake.objects.get(name="Snake 12"),
        Snake.objects.get(name="Snake 14"),
        Snake.objects.get(name="Snake 15"),
    ]


# @pytest.mark.skip("something weird in here with how we access django objects")
@mock.patch("apps.core.models.Game.update_from_engine")
@mock.patch("apps.core.engine.create")
def test_bracket_with_25_snakes(create_mock, update_mock):
    create_mock.return_value = str(uuid.uuid4())
    bracket = _arrange_tournament("single heat", 25)

    round1 = bracket.create_next_round()
    _complete_games_in_round(round1)
    round2 = bracket.create_next_round()
    _complete_games_in_round(round2)
    round3 = bracket.create_next_round()
    _complete_games_in_round(round3)
    round4 = bracket.create_next_round()
    _complete_games_in_round(round4)
    round5 = bracket.create_next_round()
    _complete_games_in_round(round5)

    assert round1.status == "complete"
    assert round2.status == "complete"
    assert round3.status == "complete"
    assert len(bracket.winners) == 3
    assert [gs.snake for gs in bracket.winners] == [
        Snake.objects.get(name="Snake 1"),
        Snake.objects.get(name="Snake 10"),
        Snake.objects.get(name="Snake 11"),
    ]
    assert [gs.snake for gs in bracket.runner_ups] == [
        Snake.objects.get(name="Snake 12"),
        Snake.objects.get(name="Snake 13"),
        Snake.objects.get(name="Snake 14"),
    ]


@mock.patch("apps.core.models.Game.update_from_engine")
@mock.patch("apps.core.engine.create")
def test_bracket_with_96_snakes(create_mock, update_mock):
    create_mock.return_value = str(uuid.uuid4())
    bracket = _arrange_tournament("single heat", 96)

    round1 = bracket.create_next_round()
    _complete_games_in_round(round1)
    round2 = bracket.create_next_round()
    _complete_games_in_round(round2)
    round3 = bracket.create_next_round()
    _complete_games_in_round(round3)
    round4 = bracket.create_next_round()
    _complete_games_in_round(round4)
    round5 = bracket.create_next_round()
    _complete_games_in_round(round5)

    assert round1.status == "complete"
    assert round2.status == "complete"
    assert round3.status == "complete"
    assert len(bracket.winners) == 3
    assert [gs.snake for gs in bracket.winners] == [
        Snake.objects.get(name="Snake 1"),
        Snake.objects.get(name="Snake 10"),
        Snake.objects.get(name="Snake 11"),
    ]
    assert [gs.snake for gs in bracket.runner_ups] == [
        Snake.objects.get(name="Snake 12"),
        Snake.objects.get(name="Snake 13"),
        Snake.objects.get(name="Snake 14"),
    ]


@mock.patch("apps.core.models.Game.update_from_engine")
@mock.patch("apps.core.engine.create")
def test_bracket_with_97_snakes(create_mock, update_mock):
    create_mock.return_value = str(uuid.uuid4())
    bracket = _arrange_tournament("single heat", 97)

    round1 = bracket.create_next_round()
    _complete_games_in_round(round1)
    round2 = bracket.create_next_round()
    _complete_games_in_round(round2)
    round3 = bracket.create_next_round()
    _complete_games_in_round(round3)
    round4 = bracket.create_next_round()
    _complete_games_in_round(round4)
    round5 = bracket.create_next_round()
    _complete_games_in_round(round5)
    round6 = bracket.create_next_round()
    _complete_games_in_round(round6)

    assert round1.status == "complete"
    assert round2.status == "complete"
    assert round3.status == "complete"
    assert round4.status == "complete"
    assert len(bracket.winners) == 3
    print([winner.__dict__ for winner in bracket.winners])
    assert bracket.winners[0].name == "Test Team 1"
    assert bracket.winners[1].name == "Test Team 10"
    assert bracket.winners[2].name == "Test Team 11"
    assert len(bracket.runner_ups) == 3
    assert bracket.runner_ups[0].name == "Test Team 12"
    assert bracket.runner_ups[1].name == "Test Team 14"
    assert bracket.runner_ups[2].name == "Test Team 16"
