# Generated by Django 3.2 on 2021-06-06 14:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("stories", "0014_auto_20210531_1916"),
    ]

    operations = [
        migrations.AlterField(
            model_name="storylocations",
            name="city",
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
