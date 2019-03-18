import time

from django.core.management.base import BaseCommand
from apps.leaderboard.jobs import SnakeRanker


class Command(BaseCommand):
    help = "Run leaderboard matches"

    def handle(self, *args, **options):
        while True:
            SnakeRanker().run()
            time.sleep(60)
