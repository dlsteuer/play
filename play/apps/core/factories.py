from apps.core.models import Game, Snake, Profile


class GameFactory:
    def basic(self, commit=False, n=None, **kwargs):
        if n:
            return [self.basic(commit=commit, **kwargs) for _ in range(n)]
        game = Game(width=20, height=20, max_turns_to_next_food_spawn=12, **kwargs)
        if commit:
            game.save()
        return game


class SnakeFactory:
    def basic(self, n=1, commit=False, profile: Profile = None):
        if profile is None:
            raise Exception("user is required")
        if n > 1:
            return [self.basic(commit=commit, profile=profile) for _ in range(n)]
        snake = Snake(name="test", url="http://foo.bar", profile=profile)
        if commit:
            snake.save()
        return snake
