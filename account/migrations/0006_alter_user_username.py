# Generated by Django 4.2 on 2023-05-07 15:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("account", "0005_remove_user_firstname_remove_user_lastname"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="username",
            field=models.CharField(max_length=255, unique=True),
        ),
    ]
