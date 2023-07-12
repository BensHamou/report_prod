# Generated by Django 4.2 on 2023-07-03 12:59

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("account", "0010_silo"),
    ]

    operations = [
        migrations.CreateModel(
            name="Horaire",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "hour_start",
                    models.IntegerField(
                        default=0,
                        validators=[
                            django.core.validators.MinValueValidator(0),
                            django.core.validators.MaxValueValidator(23),
                        ],
                    ),
                ),
                (
                    "minutes_start",
                    models.IntegerField(
                        default=0,
                        validators=[
                            django.core.validators.MinValueValidator(0),
                            django.core.validators.MaxValueValidator(59),
                        ],
                    ),
                ),
                (
                    "hour_end",
                    models.IntegerField(
                        default=0,
                        validators=[
                            django.core.validators.MinValueValidator(0),
                            django.core.validators.MaxValueValidator(23),
                        ],
                    ),
                ),
                (
                    "minutes_end",
                    models.IntegerField(
                        default=0,
                        validators=[
                            django.core.validators.MinValueValidator(0),
                            django.core.validators.MaxValueValidator(59),
                        ],
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="site",
            name="horaires",
            field=models.ManyToManyField(blank=True, to="account.horaire"),
        ),
    ]
