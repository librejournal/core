from rest_framework import serializers

from coreapp.stories.models import StoryLocations

class StoryLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoryLocations
        fields = [
            "uuid",
            "country",
            "city",
            "province_1",
            "province_2",
        ]
