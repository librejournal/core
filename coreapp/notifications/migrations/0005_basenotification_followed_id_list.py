# Generated by Django 3.2 on 2021-06-15 14:33

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("notifications", "0004_auto_20210615_1402"),
    ]

    operations = [
        migrations.AddField(
            model_name="basenotification",
            name="followed_id_list",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.IntegerField(), blank=True, null=True, size=None
            ),
        ),
    ]
