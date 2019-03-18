from django import forms
from django.db.models import Q

from apps.core.models import Snake, Game, GameSnake


class GameForm(forms.Form):
    """
        GameForm initializes a game and posts this to the engine to start the game.
    """

    board_size = forms.ChoiceField(
        choices=[
            ("small", "Small - 7x7"),
            ("medium", "Medium - 11x11"),
            ("large", "Large - 19x19"),
            ("custom", "Custom"),
        ],
        required=True,
        initial="medium",
    )
    width = forms.IntegerField(initial=11, required=False)
    height = forms.IntegerField(initial=11, required=False)
    snakes = forms.CharField(widget=forms.HiddenInput())
    engine_url = forms.CharField(required=False)

    def save(self, user):
        data = self.cleaned_data
        width = data["width"]
        height = data["height"]
        if data["board_size"] == "small":
            width = 7
            height = 7
        elif data["board_size"] == "medium":
            width = 11
            height = 11
        elif data["board_size"] == "large":
            width = 19
            height = 19

        game = Game.objects.create(
            width=width,
            height=height,
            max_turns_to_next_food_spawn=12,
            engine_url=data["engine_url"],
        )
        snake_ids = self.cleaned_data["snakes"].split(",")
        snakes = Snake.objects.filter(Q(id__in=snake_ids)).can_view(user)
        for s in snakes.all():
            game.snakes.add(s)
        for snake_id in snake_ids:
            GameSnake.objects.create(snake=snakes.get(id=snake_id), game=game)
        game.save()
        return game
