# Generated by Django 3.2 on 2021-05-01 15:29

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("files", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="file",
            name="attachment_uuid",
            field=models.UUIDField(default=uuid.uuid4, unique=True),
        ),
        migrations.AlterField(
            model_name="picture",
            name="attachment_uuid",
            field=models.UUIDField(default=uuid.uuid4, unique=True),
        ),
    ]
