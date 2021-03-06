# Generated by Django 3.2 on 2021-04-29 19:15

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("stories", "0003_auto_20210429_1914"),
    ]

    operations = [
        migrations.AlterField(
            model_name="comment",
            name="uuid",
            field=models.UUIDField(
                default=uuid.UUID("cac1f8af-e9e6-4a0c-89fd-88fdc6553fcb"), unique=True
            ),
        ),
        migrations.AlterField(
            model_name="story",
            name="uuid",
            field=models.UUIDField(
                default=uuid.UUID("d507a08c-5b74-4189-8151-3d2a719b7fc5"), unique=True
            ),
        ),
        migrations.AlterField(
            model_name="storycomponent",
            name="uuid",
            field=models.UUIDField(
                default=uuid.UUID("cae9c15e-d161-456e-b37a-44fca350e340"), unique=True
            ),
        ),
        migrations.AlterField(
            model_name="storycomponentfiles",
            name="uuid",
            field=models.UUIDField(
                default=uuid.UUID("6f76d38f-34fc-45d2-9e19-057cf1fdfaca"), unique=True
            ),
        ),
        migrations.AlterField(
            model_name="storycomponentpictures",
            name="uuid",
            field=models.UUIDField(
                default=uuid.UUID("0f5d1a33-519f-4d7e-930a-5aafd5a00010"), unique=True
            ),
        ),
        migrations.AlterField(
            model_name="storylocations",
            name="uuid",
            field=models.UUIDField(
                default=uuid.UUID("bffa47c1-8296-4afb-8019-7fed5b504793"), unique=True
            ),
        ),
        migrations.AlterField(
            model_name="storytags",
            name="uuid",
            field=models.UUIDField(
                default=uuid.UUID("014de9f3-020c-40f9-a9da-0d03393f2ed9"), unique=True
            ),
        ),
    ]
