from django.db import models, transaction

from apps.core import engine
from apps.core.models import Snake
from util.fields import ShortUUIDField
from util.models import BaseModel


class GameQuerySet(models.QuerySet):
    def watchable(self):
        return self.filter(
            status__in=(
                Game.Status.CREATED,
                Game.Status.RUNNING,
                Game.Status.STOPPED,
                Game.Status.COMPLETE,
            )
        ).exclude(engine_url__icontains="engine.internal.battlesnake.io")


class Game(BaseModel):
    """
    Game tracks a game started on the engine locally in the snake database. You
    can initialize a game through this model and call run() to start the game.
    Then, you can also call update_from_engine() at any point to refresh the
    game state from the engine onto this model.

    Creating a game looks like:

        game = Game(...) # instance created with config, ready to go
        game.create()    # game snakes created, and any other future pre-game things
        game.run()       # (OPTIONAL) sent to engine, and now it's running!
    """

    class NotCreatedError(Exception):
        pass

    class Status:
        PENDING = "pending"
        CREATED = "created"
        RUNNING = "running"
        ERROR = "error"
        STOPPED = "stopped"
        COMPLETE = "complete"

    id = ShortUUIDField(prefix="gam", max_length=128, primary_key=True)
    engine_id = models.CharField(null=True, max_length=128)
    status = models.CharField(default=Status.PENDING, max_length=30)
    turn = models.IntegerField(default=0)
    width = models.IntegerField()
    height = models.IntegerField()
    max_turns_to_next_food_spawn = models.IntegerField(default=15)
    snakes = models.ManyToManyField(Snake)
    engine_url = models.CharField(null=True, max_length=128)

    objects = GameQuerySet.as_manager()

    def config(self):
        """ Fetch the engine configuration. """
        config = {
            "width": self.width,
            "height": self.height,
            "maxTurnsToNextFoodSpawn": self.max_turns_to_next_food_spawn,
            "food": self.snakes.count(),
            "snakeTimeout": 500,
            "snakes": [
                {
                    "name": gs.name if len(gs.name) > 0 else gs.snake.public_name,
                    "url": gs.snake.url,
                    "id": gs.id,
                }
                for gs in self.gamesnake_set.all()
            ],
        }
        return config

    @transaction.atomic
    def create(self):
        """ Call the engine to create the game. Returns the game id. """
        config = self.config()
        self.engine_id = engine.create(config, self.engine_url)
        self.status = Game.Status.CREATED
        self.save()
        return self.engine_id

    def run(self):
        """ Call the engine to start the game. Returns the game id. """
        engine.run(self.engine_id, self.engine_url)
        return self.engine_id

    def engine_status(self):
        return engine.status(self.engine_id, self.engine_url)

    def update_from_engine(self):
        """ Update the status and snake statuses from the engine. """
        if self.engine_id is None:
            raise self.NotCreatedError("Game is not created")
        with transaction.atomic():
            status = engine.status(self.engine_id, self.engine_url)
            self.status = status["status"]
            self.turn = status["turn"]

            for game_snake in self.gamesnake_set.all():
                snake_status = status["snakes"][game_snake.id]
                game_snake.death = snake_status["death"]
                game_snake.save()

            self.save()
            return status

    @property
    def game_snakes(self):
        return self.gamesnake_set.all()

    def alive_game_snakes(self):
        return self.game_snakes.filter(death="pending")

    def winner(self):
        if self.status == self.Status.COMPLETE:
            living_snakes = self.alive_game_snakes()
            if living_snakes.count() == 1:
                return living_snakes.first()


class GameSnake(BaseModel):
    id = ShortUUIDField(prefix="gs", max_length=128, primary_key=True)
    snake = models.ForeignKey(Snake, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    death = models.CharField(default="pending", max_length=128)
    turns = models.IntegerField(default=0)
    name = models.CharField(default="", max_length=128)
