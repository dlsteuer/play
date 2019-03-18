import time

from django.core.management.base import BaseCommand
from apps.core.jobs import GameStatus


class Command(BaseCommand):
    help = "Update game status"

    def handle(self, *args, **options):
        while True:
            GameStatus().run()
            time.sleep(30)
