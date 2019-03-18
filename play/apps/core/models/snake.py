import logging
from urllib.parse import urljoin

import requests
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.db import models
from django.db.models import Q

from apps.core.models import Profile
from util.fields import ShortUUIDField
from util.models import BaseModel

logger = logging.getLogger(__name__)


class SnakeQuerySet(models.QuerySet):
    def can_view(self, user):
        filter_query = Q(is_public=True)
        if not user.is_anonymous:
            filter_query |= Q(profile=user.profile)
        return self.filter(filter_query)

    def by_public_name(self, name):
        if "/" in name:
            username, snake_name = name.split("/")
            return self.filter(
                Q(profile__user__username__icontains=username)
                | Q(name__icontains=snake_name)
            )
        else:
            return self.filter(
                Q(profile__user__username__icontains=name) | Q(name__icontains=name)
            )


class SnakeManager(models.Manager):
    def get_queryset(self):
        return SnakeQuerySet(self.model, using=self._db)

    def can_view(self, user):
        return self.get_queryset().can_view(user)

    def by_public_name(self, name):
        return self.get_queryset().by_public_name(name)


class Snake(BaseModel):
    id = ShortUUIDField(prefix="snk", max_length=128, primary_key=True)
    name = models.CharField(
        max_length=128, validators=[MinLengthValidator(3), MaxLengthValidator(50)]
    )
    url = models.CharField(max_length=128)
    healthy = models.BooleanField(
        default=False, verbose_name="Did this snake respond to /ping"
    )
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    is_public = models.BooleanField(
        default=False, verbose_name="Allow anyone to add this snake to a game"
    )

    objects = SnakeManager()

    @property
    def public_name(self):
        return f"{self.profile.username} / {self.name}"

    def update_healthy(self):
        url = str(self.url)
        if not url.endswith("/"):
            url = url + "/"
        ping_url = urljoin(url, "ping")
        self.healthy = False
        try:
            status_code = self.make_ping_request(ping_url)
            if status_code == 200:
                self.healthy = True
        except Exception as e:
            logger.warning(f'Failed to ping "{self}": {e}')

        self.save(update_fields=["healthy"])

    def __str__(self):
        return f"{self.public_name}"

    def make_ping_request(self, ping_url):
        response = requests.post(ping_url, timeout=1, verify=False)
        status_code = response.status_code
        return status_code

    @property
    def games(self):
        return self.game_set.all()
