from django.conf import settings
from django.utils.http import urlquote

from apps.core.models import Game


def generate_game_url(game: Game):
    engine_url = settings.ENGINE_URL
    if game.engine_url is not None and len(game.engine_url) > 0:
        engine_url = game.engine_url

    return f"{settings.BOARD_URL}/?engine={urlquote(engine_url)}&game={game.engine_id}"


def generate_exporter_url(engine_id):
    return f"{settings.EXPORTER_URL}/games/{engine_id}/gif"
