from apps.authentication.models import User
from apps.core.models import Profile


class UserFactory:
    def basic(self, email="test@test.com", commit=False):
        username = email.split("@")[0]
        user = User(username=username, email=email)
        if commit:
            Profile.objects.create(user=user)
            user.save()
        return user

    def login_as(self, client, email="test@test.com", is_admin=False):
        user = self.basic(email=email, commit=True)
        user.is_superuser = is_admin
        user.save()
        client.force_login(user, "django.contrib.auth.backends.ModelBackend")
        return user
