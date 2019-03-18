import datetime
from django.core.management import BaseCommand
from django.db import connection


class Command(BaseCommand):
    def reset_app(self, name, remove=False):
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM django_migrations WHERE app = %s", [name])
            if not remove:
                cursor.execute(
                    "INSERT INTO django_migrations (app, name, applied) VALUES (%s, %s, %s)",
                    [name, "0001_initial", datetime.datetime.now()],
                )

    def handle(self, *args, **options):
        self.reset_app("authentication")
        self.reset_app("leaderboard")
        self.reset_app("tournament")
        self.reset_app("core")
        self.reset_app("snake", remove=True)
        self.reset_app("game", remove=True)
