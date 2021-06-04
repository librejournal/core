from rest_framework import serializers

from coreapp.files.models import Picture


class UploadFileSerializer(serializers.Serializer):
    uuid = serializers.UUIDField(required=False)
    data = serializers.CharField(required=True)


class PictureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Picture
        fields = [
            "id",
            "uuid",
            "data",
        ]
        read_only_fields = [
            "id",
            "uuid",
        ]
