# Generated by Django 3.2 on 2021-04-13 16:56

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('files', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('stories', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='storytags',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tags', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='storycomponentpictures',
            name='picture',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='related_picture_components', to='files.picture'),
        ),
        migrations.AddField(
            model_name='storycomponentpictures',
            name='story_component',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pictures', to='stories.storycomponent'),
        ),
        migrations.AddField(
            model_name='storycomponentfiles',
            name='file',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='related_file_components', to='files.file'),
        ),
        migrations.AddField(
            model_name='storycomponentfiles',
            name='story_component',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='files', to='stories.storycomponent'),
        ),
        migrations.AddField(
            model_name='storycomponent',
            name='story',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='components', to='stories.story'),
        ),
        migrations.AddField(
            model_name='story',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='stories', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='story',
            name='locations',
            field=models.ManyToManyField(to='stories.StoryLocations'),
        ),
        migrations.AddField(
            model_name='story',
            name='tags',
            field=models.ManyToManyField(to='stories.StoryTags'),
        ),
        migrations.AddField(
            model_name='comment',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='comment',
            name='story',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='stories.story'),
        ),
    ]