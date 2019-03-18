import logging
from apps.core.models import Game


logger = logging.getLogger(__name__)


class GameStatus:
    """ A job that iterates over all active games and refreshes them. """

    active_statuses = (
        Game.Status.PENDING,  # TODO: Pending can be removed.
        Game.Status.CREATED,
        Game.Status.RUNNING,
        Game.Status.STOPPED,
    )

    def run(self):
        for game in Game.objects.filter(status__in=self.active_statuses):
            try:
                logger.info(f"updating game from engine id={game.id}")
                game.update_from_engine()
            except Game.NotCreatedError:
                logger.info(f"game not created id={game.id}")
            except Exception:
                game.status = Game.Status.ERROR
                game.save()
                logger.exception(f"failed to update game status id={game.id}")
