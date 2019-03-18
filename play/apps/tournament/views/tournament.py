from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.utils.encoding import escape_uri_path

from apps.authentication.decorators import admin_required, commentator_required
from apps.core.models import Game
from apps.tournament.forms import TournamentForm
from apps.tournament.models import (
    Tournament,
    TournamentBracket,
    Heat,
    HeatGame,
    Round,
    TournamentSnake,
)
from apps.utils.helpers import generate_game_url


@login_required
@admin_required
def index(request):
    user = request.user
    return render(
        request,
        "tournament/list.html",
        {
            "tournaments": Tournament.objects.all(),
            "tournament_brackets": TournamentBracket.objects.all(),
            "user": user,
        },
    )


@login_required
@admin_required
@transaction.atomic
def new(request):
    if request.method == "POST":
        form = TournamentForm(request.POST)

        if form.is_valid():
            tournament = form.save(commit=False)
            tournament.save()
            messages.success(
                request, f'Tournament "{tournament.name}" successfully created'
            )
            return redirect("/tournaments/")
    else:
        form = TournamentForm(initial={"date": datetime.now()})

    return render(request, "tournament/new.html", {"form": form})


@login_required
@admin_required
@transaction.atomic
def edit(request, tournament_id):
    tournament = Tournament.objects.get(id=tournament_id)
    if request.method == "POST":
        form = TournamentForm(request.POST, instance=tournament)

        if form.is_valid():
            t = form.save(commit=False)
            t.save()

            messages.success(request, f'Tournament group "{tournament.name}" updated')
            return redirect("/tournaments/")
    else:
        form = TournamentForm(instance=tournament)

    return render(request, "tournament/edit.html", {"form": form})


@login_required
@commentator_required
def show_current_game(request, tournament_id):
    tournament = Tournament.objects.get(id=tournament_id)
    casting_uri = tournament.casting_uri

    autoplay = request.GET.get("autoplay")
    if autoplay:
        casting_uri = f"{casting_uri}&autoplay=true"

    turn = request.GET.get("turn")
    if turn:
        casting_uri = f"{casting_uri}&turn={turn}"

    frame_rate = request.GET.get("frameRate")
    if frame_rate:
        casting_uri = f"{casting_uri}&frameRate={frame_rate}"

    if "/tree/" not in casting_uri:
        tournament.casting_uri = casting_uri

    if request.GET.get("json") == "true":
        return JsonResponse({"tournament": {"casting_uri": tournament.casting_uri}})

    return render(
        request, "tournament/show_current_game.html", {"tournament": tournament}
    )


@login_required
@admin_required
@transaction.atomic
def cast_current_game(request, tournament_id):
    tournament = Tournament.objects.get(id=tournament_id)
    heat_game = HeatGame.objects.get(id=request.POST.get("heat_game_id"))

    if heat_game.game.status in [
        Game.Status.CREATED,
        Game.Status.STOPPED,
        Game.Status.PENDING,
    ]:
        heat_game.game.run()

    title = escape_uri_path(
        f"{heat_game.heat.round.tournament_bracket.name} / Round {heat_game.heat.round.number} / Group {heat_game.heat.number} / Game {heat_game.number}"
    )
    tournament.casting_uri = (
        generate_game_url(heat_game.game)
        + f"&countdown=10&hideMediaControls=true&boardTheme=dark&frameRate=10&title={title}"
    )
    tournament.save()

    # flag previously watching games as watched
    rounds = Round.objects.filter(tournament_bracket__in=tournament.brackets)
    heats = Heat.objects.filter(round__in=rounds)
    HeatGame.objects.filter(heat__in=heats, status=HeatGame.WATCHING).update(
        status=HeatGame.WATCHED
    )

    heat_game.status = HeatGame.WATCHING
    heat_game.save()

    heat_games = HeatGame.objects.filter(heat__in=heats)
    return JsonResponse(
        {
            "heat_games": [
                {"id": hg.id, "status": hg.human_readable_status} for hg in heat_games
            ]
        }
    )


@login_required
@commentator_required
def commentator_details(request, tournament_id):
    tournament = Tournament.objects.get(id=tournament_id)
    snake_names = TournamentSnake.get_snake_names(tournament)
    snake_descriptions = TournamentSnake.get_snake_descriptions(tournament)
    return render(
        request,
        "tournament/commentator.html",
        {
            "tournament": tournament,
            "snake_names": snake_names,
            "snake_descriptions": snake_descriptions,
        },
    )
