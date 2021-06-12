from django.urls import path, include

from coreapp.files.views import UploadPictureView

urlpatterns = [
    path("api/files/upload", UploadPictureView.as_view(), name="upload-file-view"),
]
