from coreapp.coreapp.celery import app

from coreapp.notifications.processors.runner import run_new_story_processors
from coreapp.notifications.processors.notifications import (
    StoryLikeProcessor,
    CommentLikeProcessor,
)


@app.task()
def run_new_story_notifications_processor_task(story_id):
    run_new_story_processors(story_id)


@app.tasK()
def run_comment_like_processor_task(comment_id):
    CommentLikeProcessor(relation_pk=comment_id).process()


@app.task()
def run_story_like_processor_task(story_id):
    StoryLikeProcessor(relation_pk=story_id).process()
