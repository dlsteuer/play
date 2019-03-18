from django.contrib import admin
from apps.tournament.models import (
    Team,
    Tournament,
    TournamentBracket,
    TournamentSnake,
    Round,
    Heat,
    HeatGame,
)


class TeamAdmin(admin.ModelAdmin):
    search_fields = ["name"]


class HeatGameAdmin(admin.ModelAdmin):
    search_fields = ["game__engine_id"]
    fields = ["id", "status", "number"]


class TournamentSnakeAdmin(admin.ModelAdmin):
    search_fields = ["tournament__name", "bracket__name", "team__name", "snake__name"]


admin.site.register(Team, TeamAdmin)
admin.site.register(Tournament, admin.ModelAdmin)
admin.site.register(TournamentBracket, admin.ModelAdmin)
admin.site.register(TournamentSnake, TournamentSnakeAdmin)
admin.site.register(Round, admin.ModelAdmin)
admin.site.register(Heat, admin.ModelAdmin)
admin.site.register(HeatGame, HeatGameAdmin)
