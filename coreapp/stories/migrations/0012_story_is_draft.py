# Generated by Django 3.2 on 2021-05-18 18:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("stories", "0011_alter_storycomponent_type"),
    ]

    operations = [
        migrations.AddField(
            model_name="story",
            name="is_draft",
            field=models.BooleanField(default=True),
        ),
    ]
