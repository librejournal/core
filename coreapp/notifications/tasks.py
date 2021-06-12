from coreapp.coreapp.celery import app

from coreapp.notifications.processors.runner import run_new_story_processors


@app.task()
def run_new_story_notifications_processor_task(story_id):
    run_new_story_processors(story_id)
