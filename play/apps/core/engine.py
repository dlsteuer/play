import requests

from django.conf import settings


def create(config, engine_url=None):
    if engine_url is None:
        engine_url = settings.ENGINE_URL

    res = requests.post(f"{engine_url}/games", json=config)
    res.raise_for_status()
    game_id = res.json()["ID"]
    return game_id


def run(game_id, engine_url=None):
    if engine_url is None:
        engine_url = settings.ENGINE_URL

    res = requests.post(f"{engine_url}/games/{game_id}/start")
    res.raise_for_status()


def validate_snake(snake_url, engine_url=None):
    if engine_url is None:
        engine_url = settings.ENGINE_URL

    res = requests.get(f"{engine_url}/validateSnake?url={snake_url}")
    return res.json()


def status(engine_id, engine_url=None):
    # Import here to prevent circular import issue
    from apps.core.models import Game

    if engine_url is None:
        engine_url = settings.ENGINE_URL

    res = requests.get(f"{engine_url}/games/{engine_id}")
    res.raise_for_status()
    data = res.json()

    status = data["Game"].get("Status", Game.Status.PENDING)
    turn = data["LastFrame"].get("Turn", 0)
    gsnakes = data["LastFrame"].get("Snakes", [])

    snakes = {}
    for s in gsnakes:
        engine_id = s["ID"]
        snakes[engine_id] = {
            "death": s["Death"]["Cause"] if s["Death"] else Game.Status.PENDING,
            "turn": s["Death"]["Turn"] if s["Death"] else turn,
        }

    return {"status": status, "turn": turn, "snakes": snakes}
