from django import forms

from apps.core.models import Snake, Profile


class SnakeForm(forms.ModelForm):
    class Meta:
        model = Snake
        fields = ["name", "url", "is_public"]

    def __init__(self, profile: Profile, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.profile = profile

    def clean(self):
        cleaned_data = super().clean()
        try:
            name = cleaned_data["name"]

            # need to filter here, in case we already have a profile with multiple snakes with the same name
            snakes = self.profile.snakes.filter(name=name)
            if self.instance is not None:
                snakes = snakes.exclude(id=self.instance.id)
            if snakes.count() > 0:
                raise forms.ValidationError(
                    f"{self.profile.username}/{name} already exists."
                )
        except Snake.DoesNotExist:
            pass

    def save(self, commit=True):
        snake = super().save(commit=False)
        snake.profile = self.profile
        if commit is True:
            snake.save()
        return snake
