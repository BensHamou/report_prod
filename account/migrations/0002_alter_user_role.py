# Generated by Django 4.2 on 2023-05-03 15:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("account", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="role",
            field=models.CharField(
                choices=[
                    ("Gestionnaire de production", "Gestionnaire de production"),
                    ("Gestionnaire de stock", "Gestionnaire de stock"),
                    ("Responsable de production", "Responsable de production"),
                ],
                max_length=30,
            ),
        ),
    ]
