from django.db import models

from util.fields import CreatedDateTimeField, ModifiedDateTimeField


class BaseManager(models.Manager):
    def get_or_init(self, defaults=None, **kwargs):
        try:
            return self.get(**kwargs), False
        except self.model.DoesNotExist:
            defaults = defaults or {}
            defaults.update(kwargs)
            return self.model(**defaults), True


class BaseModel(models.Model):
    created = CreatedDateTimeField()
    modified = ModifiedDateTimeField()

    objects = BaseManager()

    class Meta:
        abstract = True

    def is_saved(self):
        return not self._state.adding
