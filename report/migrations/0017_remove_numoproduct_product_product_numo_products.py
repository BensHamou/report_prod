# Generated by Django 4.2 on 2023-06-26 13:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("report", "0016_numoproduct"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="numoproduct",
            name="product",
        ),
        migrations.AddField(
            model_name="product",
            name="numo_products",
            field=models.ManyToManyField(blank=True, to="report.numoproduct"),
        ),
    ]
