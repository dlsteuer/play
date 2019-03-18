import csv

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse

from apps.authentication.decorators import admin_required
from apps.tournament.forms import TournamentBracketForm
from apps.tournament.models import (
    Tournament,
    TournamentBracket,
    TournamentSnake,
    Round,
    Heat,
    HeatGame,
    PreviousGameTiedException,
    DesiredGamesReachedValidationError,
    RoundNotCompleteException,
)


@login_required
@admin_required
@transaction.atomic
def new(request, tournament_id):
    tournament = Tournament.objects.get(id=tournament_id)

    if request.method == "POST":
        form = TournamentBracketForm(request.POST)

        if form.is_valid():
            bracket = form.save(commit=False)
            bracket.tournament = tournament
            bracket.save()

            messages.success(
                request, f'Tournament "{tournament.name}" successfully created'
            )
            return redirect("/tournaments/")
    else:
        form = TournamentBracketForm()
    return render(
        request, "tournament_bracket/new.html", {"form": form, "tournament": tournament}
    )


@login_required
@admin_required
@transaction.atomic
def edit(request, bracket_id):
    tournament_bracket = TournamentBracket.objects.get(id=bracket_id)
    if request.method == "POST":
        form = TournamentBracketForm(request.POST, instance=tournament_bracket)

        if form.is_valid():
            bracket = form.save(commit=False)
            bracket.save()

            for ts in TournamentSnake.objects.filter(bracket=tournament_bracket):
                ts.delete()

            messages.success(
                request, f'Tournament Bracket "{tournament_bracket.name}" updated'
            )
            return redirect("/tournaments/")
    else:
        form = TournamentBracketForm(instance=tournament_bracket)

    return render(request, "tournament_bracket/edit.html", {"form": form})


@login_required
@admin_required
def show(request, bracket_id):
    tournament_bracket = TournamentBracket.objects.get(id=bracket_id)
    snake_names = TournamentSnake.get_snake_names(tournament_bracket.tournament)
    return render(
        request,
        "tournament_bracket/show.html",
        {"tournament_bracket": tournament_bracket, "snake_names": snake_names},
    )


@login_required
@admin_required
def show_csv(request, bracket_id):
    tournament_bracket = TournamentBracket.objects.get(id=bracket_id)
    # Create the HttpResponse object with the appropriate CSV header.
    filename = f"{tournament_bracket.tournament.name}_{tournament_bracket.name}.csv"
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    writer = csv.writer(response)
    for row in tournament_bracket.export():
        writer.writerow(row)

    return response


@login_required
@admin_required
def create_next_round(request, bracket_id):
    tournament_bracket = TournamentBracket.objects.get(id=bracket_id)
    try:
        tournament_bracket.create_next_round()
    except RoundNotCompleteException as e:
        messages.error(request, e.message)
    return redirect(
        reverse("tournament_bracket", kwargs={"bracket_id": tournament_bracket.id})
    )


@login_required
@admin_required
def update_game_statuses(request, bracket_id):
    tournament_bracket = TournamentBracket.objects.get(id=bracket_id)
    tournament_bracket.update_heat_games()
    return redirect(
        reverse("tournament_bracket", kwargs={"bracket_id": tournament_bracket.id})
    )


@login_required
@admin_required
def create_game(request, bracket_id, heat_id):
    tournament_bracket = TournamentBracket.objects.get(id=bracket_id)
    heat = Heat.objects.get(id=heat_id)
    try:
        heat.create_next_game()
    except PreviousGameTiedException:
        messages.error(request, "Previous game tied; It must be rerun.")
    except DesiredGamesReachedValidationError:
        messages.error(request, "Shouldn't create another game for this heat")
    except Exception as e:
        import traceback

        traceback.print_tb(e.__traceback__)
        messages.error(request, e.__str__())
    return redirect(
        reverse("tournament_bracket", kwargs={"bracket_id": tournament_bracket.id})
    )


@login_required
@admin_required
def delete_game(request, bracket_id, heat_id, heat_game_number):
    tournament_bracket = TournamentBracket.objects.get(id=bracket_id)
    heat_game = HeatGame.objects.get(heat_id=heat_id, number=heat_game_number)
    heat_game.delete()
    return redirect(
        reverse("tournament_bracket", kwargs={"bracket_id": tournament_bracket.id})
    )


@login_required
@admin_required
def run_heat_game(request, heat_id, heat_game_number):
    heat_game = HeatGame.objects.get(heat_id=heat_id, number=heat_game_number)
    if heat_game.game is None or heat_game.game.engine_id is None:
        heat_game.game.create()
        heat_game.game.run()

    autoplay = request.GET.get("autoplay")
    if autoplay:
        return redirect(
            reverse("game", kwargs={"engine_id": heat_game.game.engine_id})
            + f"?autoplay={autoplay}"
        )

    return redirect(reverse("game", kwargs={"engine_id": heat_game.game.engine_id}))


@login_required
@admin_required
def tree(request, bracket_id):
    tournament_bracket = TournamentBracket.objects.get(id=bracket_id)
    snake_names = TournamentSnake.get_snake_names(tournament_bracket.tournament)
    return render(
        request,
        "tournament_bracket/tree.html",
        {"bracket": tournament_bracket, "snake_names": snake_names},
    )


@login_required
@admin_required
def cast_page(request, bracket_id):
    tournament_bracket = TournamentBracket.objects.get(id=bracket_id)
    if request.GET.get("page") == "tree":
        # flag previously watching games as watched
        rounds = Round.objects.filter(
            tournament_bracket__in=tournament_bracket.tournament.brackets
        )
        heats = Heat.objects.filter(round__in=rounds)
        HeatGame.objects.filter(heat__in=heats, status=HeatGame.WATCHING).update(
            status=HeatGame.WATCHED
        )

        tournament_bracket.tournament.casting_uri = reverse(
            "tournament_bracket_tree", kwargs={"bracket_id": tournament_bracket.id}
        )
        tournament_bracket.tournament.save()
    else:
        tournament_bracket.update_heat_games()

    return redirect(
        reverse("tournament_bracket", kwargs={"bracket_id": tournament_bracket.id})
    )
