from django.core.management import BaseCommand

from apps.tournament.models import Tournament
from apps.core.models import Snake

import time
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Ping snakes"

    def handle(self, *args, **options):
        import urllib3

        urllib3.disable_warnings()
        while True:
            self.test_all_snakes(False)
            logger.info("sleeping for 10s")
            time.sleep(10)

    def test_all_snakes(self, only_tournament_snakes):
        snakes = []
        if only_tournament_snakes:
            snakes = Snake.objects.filter(
                tournament__in=Tournament.objects.all()
            ).distinct()
        else:
            snakes = Snake.objects.all()

        for snake in snakes:
            start = time.time()
            snake.update_healthy()
            end = time.time()
            totalTime = int(round((end - start) * 1000))
            logger.info(
                f"pinging snake: {snake}... "
                + ("healthy" if snake.healthy else "unhealthy")
                + f" in ({totalTime}ms)"
                + (" slow-snake" if totalTime > 500 else "")
            )
