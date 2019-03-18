from datetime import datetime

from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect

from apps.core.models import Profile
from apps.tournament.models import Team


def with_current_team(action):
    def decorate(request, *args, **kwargs):
        try:
            team = Team.objects.get(team_members=request.user.profile)
            request.team = team
            return action(request, *args, **kwargs)
        except Team.DoesNotExist:
            return redirect("/team/new")

    return decorate


def msg_once(request, msg, msg_func):
    if msg not in [m.message for m in messages.get_messages(request)]:
        msg_func(request, msg)


def check_team_tournament_status(request):
    if request.user.is_superuser:
        return

    profile = request.user.profile
    utc_now = datetime.utcnow()
    today = datetime(year=utc_now.year, month=utc_now.month, day=utc_now.day)
    if settings.TOURNAMENT_DATE is not None and settings.TOURNAMENT_DATE != today:
        return

    if profile.team_set.count() > 0:
        team = profile.team_set.first()
        ts = team.tournament_snakes.first()
        if ts is None:
            return
        time = settings.TOURNAMENT_START_TIME
        if not ts.snake.healthy:
            msg_once(
                request,
                f"{team.name}, your snake, {ts.snake.name}, is not responding to ping checks. "
                f"Tournament starts at {time} so get it working by then.",
                messages.warning,
            )
        else:
            msg_once(
                request,
                f"{team.name}, your snake, {ts.snake.name}, is responding to ping checks. "
                f"Good luck in the {ts.bracket.name} bracket."
                f"Tournament starts at {time}.",
                messages.info,
            )
    elif (
        get_client_ip(request) in settings.TOURNAMENT_CONFERENCE_IPS
        and profile.team_set.count() == 0
    ):
        msg_once(
            request,
            f"{request.user.username}, your GitHub account is not yet associated with a team!  "
            f"When you have formed a team and have a working snake, please come see the registration desk.  "
            f"Registration closes at {settings.TOURNAMENT_REGISTRATION_CLOSE}",
            messages.warning,
        )


def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


def tournament_notifications_middleware(get_response):
    def middleware(request):

        try:
            profile = request.user.profile if not request.user.is_anonymous else None

            if not request.user.is_anonymous and profile is not None:
                check_team_tournament_status(request)
        except Profile.DoesNotExist:
            pass

        response = get_response(request)
        return response

    return middleware
