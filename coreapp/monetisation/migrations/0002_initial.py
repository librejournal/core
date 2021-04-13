# Generated by Django 3.2 on 2021-04-13 16:56

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('monetisation', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscription',
            name='subscribed_to',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subs', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='subscription',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subscribed_to', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='donation',
            name='donator',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='given_donations', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='donation',
            name='reciever',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recieved_donations', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='adrevenue',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='revenue', to=settings.AUTH_USER_MODEL),
        ),
    ]
