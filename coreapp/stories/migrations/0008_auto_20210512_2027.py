# Generated by Django 3.2 on 2021-05-12 20:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("stories", "0007_auto_20210512_2024"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="commentlikes",
            name="dislike",
        ),
        migrations.RemoveField(
            model_name="commentlikes",
            name="like",
        ),
        migrations.RemoveField(
            model_name="storylikes",
            name="dislike",
        ),
        migrations.RemoveField(
            model_name="storylikes",
            name="like",
        ),
        migrations.AddField(
            model_name="commentlikes",
            name="is_like",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="storylikes",
            name="is_like",
            field=models.BooleanField(default=True),
        ),
    ]
