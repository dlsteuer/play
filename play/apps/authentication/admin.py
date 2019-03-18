from django.contrib import admin
from django.contrib.auth.models import Group

from social_django.models import Association, Nonce, UserSocialAuth

from apps.authentication.models import User


class UserAdmin(admin.ModelAdmin):
    search_fields = ["username"]
    ordering = ["username"]


admin.site.unregister(Association)
admin.site.unregister(Nonce)
admin.site.unregister(UserSocialAuth)
admin.site.unregister(Group)

admin.site.register(User, UserAdmin)
