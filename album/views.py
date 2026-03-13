import os
import uuid
import traceback

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from .models import Photo
from .forms import PhotoForm
from .supabase_client import get_client


def photo_list(request):
    sort = request.GET.get("sort", "date")
    if sort == "name":
        photos = Photo.objects.order_by("name")
    else:
        photos = Photo.objects.order_by("-uploaded_at")
    return render(request, "album/photo_list.html", {"photos": photos, "sort": sort})


def photo_detail(request, pk):
    photo = get_object_or_404(Photo, pk=pk)
    return render(request, "album/photo_detail.html", {"photo": photo})


@login_required
def photo_upload(request):
    if request.method == "POST":
        form = PhotoForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                sb = get_client()
                bucket = os.environ.get("SUPABASE_BUCKET", "photos")

                file_obj = form.cleaned_data["image"]
                file_ext = file_obj.name.split(".")[-1].lower()
                storage_path = f"{uuid.uuid4()}.{file_ext}"

                file_bytes = file_obj.read()

                sb.storage.from_(bucket).upload(
                    storage_path,
                    file_bytes,
                    file_options={"content-type": file_obj.content_type},
                )

                public_url = sb.storage.from_(bucket).get_public_url(storage_path)

                photo = form.save(commit=False)
                photo.image_url = public_url
                photo.storage_path = storage_path
                photo.save()

                return redirect("photo_list")

            except Exception as e:
                print("UPLOAD ERROR:", repr(e))
                print(traceback.format_exc())
                return render(request, "album/upload.html", {"form": form, "error": str(e)}, status=500)
    else:
        form = PhotoForm()

    return render(request, "album/upload.html", {"form": form})


@login_required
def photo_delete(request, pk):
    photo = get_object_or_404(Photo, pk=pk)
    if request.method == "POST":
        try:
            sb = get_client()
            bucket = os.environ.get("SUPABASE_BUCKET", "photos")
            sb.storage.from_(bucket).remove([photo.storage_path])
            photo.delete()
            return redirect("photo_list")
        except Exception as e:
            print("DELETE ERROR:", repr(e))
            print(traceback.format_exc())
            messages.error(request, f"Delete failed: {e}")
            return redirect("photo_delete", pk=photo.pk)
    return render(request, "album/photo_delete.html", {"photo": photo})


def register(request):
    if request.user.is_authenticated:
        return redirect("photo_list")

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("photo_list")
    else:
        form = UserCreationForm()
    return render(request, "registration/register.html", {"form": form})


@require_POST
def logout_view(request):
    logout(request)
    return redirect("photo_list")
