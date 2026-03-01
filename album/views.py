import os, uuid
from django.shortcuts import render, redirect, get_object_or_404
from .models import Photo
from .forms import PhotoForm
from .supabase_client import get_client

import traceback
from django.http import HttpResponseServerError
from django.shortcuts import render, redirect, get_object_or_404


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

def upload_photo(request):
    if request.method == "POST":
        form = PhotoForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # mindent ide, még a kliens initet is!
                sb = get_client()
                bucket = os.environ.get("SUPABASE_BUCKET", "photos")

                file_obj = request.FILES["image"]
                file_ext = file_obj.name.split(".")[-1].lower()
                storage_path = f"{uuid.uuid4()}.{file_ext}"

                file_bytes = file_obj.read()

                res = sb.storage.from_(bucket).upload(
                    storage_path,
                    file_bytes,
                    file_options={"content-type": file_obj.content_type},
                )

                public_url = sb.storage.from_(bucket).get_public_url(storage_path)

                photo = form.save(commit=False)
                photo.image_url = public_url
                photo.storage_path = storage_path
                photo.save()

                return redirect("index")

            except Exception as e:
                print("UPLOAD ERROR:", repr(e))
                print(traceback.format_exc())
                # ezt is megmutathatod debugra:
                return render(request, "album/upload.html", {"form": form, "error": str(e)}, status=500)

    else:
        form = PhotoForm()

    return render(request, "album/upload.html", {"form": form})

def photo_delete(request, pk):
    photo = get_object_or_404(Photo, pk=pk)
    if request.method == "POST":
        photo.delete()
        return redirect("photo_list")
    return render(request, "album/photo_delete.html", {"photo": photo})