class SnakeLeaderboardPresenter:
    def __init__(self, snake_leaderboard):
        self.snake_leaderboard = snake_leaderboard

    @property
    def id(self):
        return self.snake_leaderboard.id

    @property
    def snake(self):
        return self.snake_leaderboard.snake

    @property
    def rank(self):
        return self.snake_leaderboard.rank

    @property
    def results(self):
        return self.snake_leaderboard.leaderboardresult_set.order_by(
            "-modified"
        ).prefetch_related("game")[:5]
