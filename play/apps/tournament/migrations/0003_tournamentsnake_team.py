# Generated by Django 2.0.10 on 2019-02-14 07:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [("tournament", "0002_auto_20190214_0727")]

    operations = [
        migrations.AddField(
            model_name="tournamentsnake",
            name="team",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="tournament.Team",
            ),
        )
    ]
