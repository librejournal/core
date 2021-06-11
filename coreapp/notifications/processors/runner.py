from coreapp.notifications.processors.notifications import (
    StoryLikeProcessor,
    CommentLikeProcessor,
    NewStoryByAuthorProcessor,
    NewStoryByLocationProcessor,
    NewStoryByTagProcessor,
)

def run_new_story_processors(story_id):
    processors = [
        NewStoryByAuthorProcessor(relation_pk=story_id),
        NewStoryByLocationProcessor(relation_pk=story_id),
        NewStoryByTagProcessor(relation_pk=story_id),
    ]
    for processor in processors:
        processor.process()
