# Generated by Django 3.2 on 2021-05-31 19:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("files", "0003_auto_20210531_1916"),
        ("stories", "0013_auto_20210521_1839"),
    ]

    operations = [
        migrations.AddField(
            model_name="story",
            name="thumbnail",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="stories",
                to="files.picture",
            ),
        ),
        migrations.AddField(
            model_name="story",
            name="title",
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
        migrations.AddField(
            model_name="storycomponent",
            name="picture",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="components",
                to="files.picture",
            ),
        ),
    ]
