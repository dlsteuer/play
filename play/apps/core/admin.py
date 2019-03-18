from django.contrib import admin
from apps.core.models import Profile, Game, Snake


class GameAdmin(admin.ModelAdmin):
    list_display = ["engine_id", "width", "height", "status", "turn"]
    search_fields = ["engine_id", "id"]


class SnakeAdmin(admin.ModelAdmin):
    search_fields = ["profile__user__username", "name"]
    ordering = ["profile__user__username", "name"]
    autocomplete_fields = ("profile",)
    list_display = ["public_name", "is_public"]


class ProfileAdmin(admin.ModelAdmin):
    search_fields = ["user__username"]
    autocomplete_fields = ("user",)


admin.site.register(Snake, SnakeAdmin)
admin.site.register(Game, GameAdmin)
admin.site.register(Profile, ProfileAdmin)
