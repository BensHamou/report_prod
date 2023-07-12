# Generated by Django 4.2 on 2023-07-03 17:08

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("report", "0023_remove_report_passed_time"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="arret",
            name="duration",
        ),
        migrations.AddField(
            model_name="arret",
            name="hour",
            field=models.IntegerField(
                default=0,
                validators=[
                    django.core.validators.MinValueValidator(0),
                    django.core.validators.MaxValueValidator(23),
                ],
            ),
        ),
        migrations.AddField(
            model_name="arret",
            name="minutes",
            field=models.IntegerField(
                default=0,
                validators=[
                    django.core.validators.MinValueValidator(0),
                    django.core.validators.MaxValueValidator(59),
                ],
            ),
        ),
    ]
