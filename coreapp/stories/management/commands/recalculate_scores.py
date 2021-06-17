import logging

from django.core.management import BaseCommand

from coreapp.users.models import Profile, ProfileStatistics
from coreapp.stories.models import Story

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Update profile stats."

    def handle(self, *args, **options):
        to_update = []
        for profile in Profile.objects.all().iterator():
            story_count = Story.objects.filter(author=profile).count()
            stats_obj = profile.profile_statistics
            stats_obj.reputation = profile.weighted_profile_score
            stats_obj.number_of_posts = story_count
            to_update.append(stats_obj)
            logger.debug("Updated stats for Profile(id=%s)", profile.id)
        ProfileStatistics.objects.bulk_update(
            to_update,
            [
                "reputation",
                "number_of_posts",
            ],
        )
        logger.debug("Update complete!")
