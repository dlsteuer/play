from django.shortcuts import redirect
from django.urls import reverse


def profile_required(action):
    """
    Redirects to an edit profile page which will activate the profile.
    """

    def middleware(request, *args, **kwargs):
        if not request.user.is_anonymous and not hasattr(request.user, "profile"):
            return redirect(reverse("settings"))
        return action(request, *args, **kwargs)

    return middleware
