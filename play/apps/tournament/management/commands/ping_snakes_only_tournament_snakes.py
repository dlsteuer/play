from apps.tournament.management.commands.ping_snakes import Command as CommandSnakes
import time
import logging

logger = logging.getLogger(__name__)


class Command(CommandSnakes):
    help = "Ping snakes that are in a tournament"

    def handle(self, *args, **options):
        while True:
            self.test_all_snakes(True)
            logger.info("sleeping for 10s")
            time.sleep(10)
