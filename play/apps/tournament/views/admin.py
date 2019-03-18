from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect

from apps.authentication.decorators import admin_required
from apps.authentication.models import User
from apps.core import engine
from apps.core.models import Snake
from apps.tournament.forms import EditTeamForm
from apps.tournament.models import Team


@login_required
@admin_required
def index(request):
    return render(request, "admin/search.html")


@login_required
@admin_required
def find_teams(request):
    teams = Team.objects.filter(name__icontains=request.GET.get("q", ""))
    return JsonResponse(
        [{"value": team.id, "text": f"{team.name}"} for team in teams], safe=False
    )


@login_required
@admin_required
def new_team(request):
    form = EditTeamForm()
    return render(request, "admin/edit_team.html", {"form": form})


@login_required
@admin_required
def edit_team(request, team_id):
    team = Team.objects.get(id=team_id)
    ts = team.tournament_snakes.first()
    u = [profile.user.id for profile in team.team_members.all()]
    initial = {}
    if ts is not None:
        initial = {
            "snakes": ts.snake.id,
            "users": ",".join(u),
            "tournament": f"{ts.tournament.id}/{ts.bracket.id}",
        }
    form = EditTeamForm(instance=team, initial=initial)
    return render(request, "admin/edit_team.html", {"form": form})


@login_required
@admin_required
def update_team(request, team_id=None):
    team = None
    if team_id is not None:
        team = Team.objects.get(id=team_id)
    form = EditTeamForm(request.POST, instance=team)
    if form.is_valid():
        form.save()
        return redirect("/tournament/admin")
    return render(request, "admin/edit_team.html", {"form": form})


@login_required
@admin_required
def users(request):
    q = request.GET.get("q", "")
    u = User.objects.filter(username__icontains=q).order_by("username")
    return JsonResponse(
        [{"value": user.id, "text": f"{user.username}"} for user in u], safe=False
    )


@login_required
@admin_required
def user_info(request):
    user_ids = request.GET.get("users", "").split(",")
    u = User.objects.filter(id__in=user_ids).order_by("username")
    return JsonResponse(
        [{"value": user.id, "text": f"{user.username}"} for user in u], safe=False
    )


@login_required
@admin_required
def snakes(request):
    user_ids = request.GET.get("users", "").split(",")
    s = Snake.objects.filter(profile__user__id__in=user_ids).order_by(
        "profile__user__username", "name"
    )
    return JsonResponse(
        [
            {"value": snake.id, "text": f"{snake.profile.username}/{snake.name}"}
            for snake in s
        ],
        safe=False,
    )


@login_required
@admin_required
def snake_status(request, snake_id):
    s = Snake.objects.get(id=snake_id)
    return JsonResponse(engine.validate_snake(s.url))
