# Generated by Django 3.2 on 2021-06-15 06:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("notifications", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="notification",
            name="is_read",
            field=models.BooleanField(db_index=True, default=False),
        ),
    ]
