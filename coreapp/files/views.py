from django.shortcuts import render

from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from coreapp.files.serializers import PictureSerializer
from coreapp.files.models import Picture


class UploadPictureView(GenericAPIView):
    serializer_class = PictureSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        received_file = request.FILES["file"]
        pic = Picture.objects.create(data=received_file.read())
        return Response({"id": pic.id})
