from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test


def admin_required(
    function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None
):
    """
    Decorator for views that checks that the user is logged in and an admin, redirecting
    to the log-in page if necessary.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_admin,
        login_url=login_url,
        redirect_field_name=redirect_field_name,
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


def commentator_required(
    function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None
):
    """
        Decorator for views that checks that the user is logged in, and a commentator or an admin, redirecting
        to the log-in page if necessary.
        """
    actual_decorator = user_passes_test(
        lambda u: u.is_commentator or u.is_admin,
        login_url=login_url,
        redirect_field_name=redirect_field_name,
    )
    if function:
        return actual_decorator(function)
    return actual_decorator
