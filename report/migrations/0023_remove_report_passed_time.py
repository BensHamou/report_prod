# Generated by Django 4.2 on 2023-07-03 16:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("report", "0022_alter_report_shift"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="report",
            name="passed_time",
        ),
    ]
