from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render

from apps.authentication.decorators import admin_required
from apps.authentication.models import User
from apps.core.models import Snake, Game


@login_required
@admin_required
def show(request):
    context = {}

    # Load up these values with whatever you want to see on the page.
    # Test fancy values with:
    #   import random
    #   random.randint(0, 100000)

    context["total_users"] = User.objects.all().count()
    context["total_snakes"] = Snake.objects.all().count()
    context["total_games"] = Game.objects.all().count()

    if request.GET.get("json") == "true":
        return JsonResponse(context)

    return render(request, "core/stats.html")
