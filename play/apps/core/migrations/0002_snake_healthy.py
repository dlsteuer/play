# Generated by Django 2.0.10 on 2019-02-10 17:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("core", "0001_initial")]

    operations = [
        migrations.AddField(
            model_name="snake",
            name="healthy",
            field=models.BooleanField(
                default=False, verbose_name="Did this snake respond to /ping"
            ),
        )
    ]