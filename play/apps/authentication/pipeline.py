from social_core.exceptions import AuthForbidden


def blacklist_usernames(backend, details, response, *args, **kwargs):
    # We reserve these usernames for our own purposes.
    if kwargs.get("username") in ["battlesnake", "battlesnakeio"]:
        raise AuthForbidden(backend)
