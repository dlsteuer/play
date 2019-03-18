from settings.base import *  # noqa: F403

import os

# Force test DB to use SQLite
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),  # noqa: F405
    }
}

# Null these out to avoid hitting them in tests.
ENGINE_URL = ""
BOARD_URL = ""
