from django.urls import path
from . import views

urlpatterns = [
    path("", views.photo_list, name="photo_list"),
    path("upload/", views.upload_photo, name="photo_upload"),
    path("photo/<int:pk>/", views.photo_detail, name="photo_detail"),
    path("photo/<int:pk>/delete/", views.photo_delete, name="photo_delete"),
]