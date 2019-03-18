from datetime import datetime, timedelta
from django import forms
from django.db import transaction
from django.forms import ValidationError

from apps.authentication.models import User
from apps.core.models import Snake
from apps.tournament.models import Team, TournamentBracket, Tournament, TournamentSnake


class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ["name", "description"]

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        self.fields["description"].label = "Team Backstory"

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data

    def save(self, *args, **kwargs):
        team = super().save(commit=False)
        team.save()

        team.team_members.add(self.user.profile)
        team.save()
        return team


def get_edit_team_tournament_choices():
    choices = []
    for t in Tournament.objects.filter(date__gte=(datetime.now() + timedelta(days=-2))):
        for tb in t.brackets.all():
            choices.append((f"{t.id}/{tb.id}", f"{t.name}/{tb.name}"))
    return choices


def null_validator():
    pass


class EditTeamForm(forms.ModelForm):
    users = forms.CharField(widget=forms.HiddenInput())
    snakes = forms.CharField(widget=forms.HiddenInput())
    tournament = forms.ChoiceField(choices=get_edit_team_tournament_choices)
    status = forms.CharField(widget=forms.Textarea(), disabled=True, required=False)

    class Meta:
        model = Team
        fields = ["name", "description"]

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get("name", "")

        # Allow editing of a Team instance
        if not self.instance:
            try:
                Team.objects.get(name__iexact=name)
                raise forms.ValidationError(f"Team {name} already exists.")
            except Team.DoesNotExist:
                pass

        if len(cleaned_data.get("users", "")) == 0:
            raise forms.ValidationError(f"At least 1 user must be on a team.")

        user_ids = self.cleaned_data.get("users", "").split(",")
        profiles = [u.profile for u in User.objects.filter(id__in=user_ids)]

        teams = Team.objects.filter(team_members__in=profiles).exclude(
            id=(self.instance.id if self.instance is not None else None)
        )
        if teams.count() > 0:
            raise forms.ValidationError(f"Some users are already on a team.")

        if len(cleaned_data["snakes"]) == 0:
            raise forms.ValidationError(f"Please select a snake")

    @transaction.atomic
    def save(self, **kwargs):
        team = super().save(**kwargs)
        for ts in team.tournament_snakes.all():
            ts.delete()

        for tm in team.team_members.all():
            team.team_members.remove(tm)

        user_ids = self.cleaned_data["users"].split(",")
        users = User.objects.filter(id__in=user_ids)
        found = False
        for user in users:
            team.team_members.add(user.profile)
            if user.profile.snakes.filter(id=self.cleaned_data["snakes"]).count() > 0:
                found = True

        if not found:
            raise forms.ValidationError(
                "Snake chosen must belong to a user on the team."
            )

        t = self.cleaned_data["tournament"].split("/")
        tb = TournamentBracket.objects.get(tournament_id=t[0], id=t[1])
        snake = Snake.objects.get(id=self.cleaned_data["snakes"])

        TournamentSnake.objects.create(
            tournament=tb.tournament, bracket=tb, snake=snake, team=team
        )


class AddTeamMemberForm(forms.Form):
    username = forms.CharField(required=True)

    def __init__(self, user, team, *args, **kwargs):
        self.user = user
        self.team = team
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        try:
            cleaned_data["user"] = User.objects.get(username=username)
        except User.DoesNotExist:
            raise ValidationError(
                f"Hmm, {username} can't be found. Have they logged in yet?"
            )

        try:
            # If this lookup raises an exception, then we can continue
            team_name = cleaned_data["user"].profile.team_set.get(id=self.team.id).name
            raise ValidationError(f"{username} already belongs to team {team_name}")
        except Team.DoesNotExist:
            pass

        return cleaned_data

    def save(self, *args, **kwargs):
        return self.team.team_members.add(self.cleaned_data["user"].profile)


class TournamentBracketForm(forms.ModelForm):
    class Meta:
        model = TournamentBracket
        fields = [
            "name",
            "board_width",
            "board_height",
            "board_food",
            "board_max_turns_to_next_food_spawn",
        ]


class TournamentForm(forms.ModelForm):
    class Meta:
        model = Tournament
        fields = ["name", "date", "status", "engine_url"]


class TournamentSnakeForm(forms.ModelForm):
    def __init__(self, user, tournament, snake, bracket, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.team = user.profile.team_set.first()
        self.user = user
        self.snake = snake
        self.tournament = tournament
        self.fields["snake"].choices = [(s.id, s.name) for s in self.team.snakes]
        self.initial["snake"] = snake
        self.fields["bracket"].choices = [
            (b.id, b.name) for b in self.tournament.brackets
        ]
        self.initial["bracket"] = bracket

    def is_valid(self):
        return self.tournament.status == Tournament.REGISTRATION

    def save(self, *args, **kwargs):
        qs = TournamentSnake.objects.filter(
            snake__in=self.team.snakes, tournament=self.tournament
        )
        qs.delete()

        ts, _ = TournamentSnake.objects.get_or_create(
            snake=self.snake, bracket=self.bracket, tournament=self.tournament
        )
        return ts

    class Meta:
        model = TournamentSnake
        fields = ["bracket", "snake"]
