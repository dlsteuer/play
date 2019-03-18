from urllib.parse import urlencode

from django.shortcuts import redirect
from django.urls import path

from apps.pages import views


def direct(path):
    def redirector(request):
        query_string = urlencode(request.GET)
        url = f"{path}"
        if query_string:
            url = f"{url}?{query_string}"
        return redirect(url)

    return redirector


blog = "https://medium.com/battlesnake"
docs = "https://docs.battlesnake.io"
events = "https://events.battlesnake.io"
github = "https://github.com/battlesnakeio"
slack = "https://join.slack.com/t/battlesnake/shared_invite/enQtMzQ1MjIyNDAzNzgxLTJkYTQyZGM5NTYyMjI3MGZkN2U4ZTEyMGFhYjM2MzQ3NzEyOTM1N2ZhZjgwMGFlZDM0YWNiZmRhMmVkMDZkOGE"
twitter = "https://twitter.com/battlesnakeio"
twitch = "https://twitch.tv/battlesnakeio"

urlpatterns = [
    path("about/faq/", views.faq, name="faq"),
    path("about/mission/", views.mission, name="mission"),
    path("about/diversity/", views.diversity, name="diversity"),
    path("about/conduct/", views.conduct, name="conduct"),
    path("blog/", direct(blog), name="blog"),
    path("error/404/", views.error400, name="400"),
    path("error/404/", views.error403, name="403"),
    path("error/404/", views.error404, name="404"),
    path("error/500/", views.error500, name="500"),
    path("help/", views.help, name="help"),
    path("learn/", views.learn),
    path("privacy/", views.privacy, name="privacy"),
    path("report/", views.report, name="report"),
    path("terms/", views.terms, name="terms"),
    # Event specific redirects:
    path("host-event/", direct(f"{events}/host-event")),
    path("resources/", direct(f"{events}/resources/"), name="resources"),
    path("tournament/", direct(f"{events}/tournament"), name="tournament"),
    # Aliases for convenience:
    path("docs/", direct(docs), name="docs"),
    path("events/", direct(events), name="events"),
    path("events/sponsors/", direct(f"{events}/sponsorship"), name="sponsors"),
    path("github/", direct(f"{github}/community"), name="github"),
    path("slack/", direct(slack), name="slack"),
    path("twitch/", direct(twitch), name="twitch"),
    path("twitter/", direct(twitter), name="twitter"),
]
