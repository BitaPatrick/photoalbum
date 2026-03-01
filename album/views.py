import os
import uuid
import logging
from django.shortcuts import render, redirect
from .models import Photo
from .forms import PhotoForm
from .supabase_client import get_client

logger = logging.getLogger(__name__)

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


def photo_upload(request):
    if request.method == "POST":
        form = PhotoForm(request.POST, request.FILES)
        if form.is_valid():
            file_obj = request.FILES["image"]
            filename = f"{uuid.uuid4()}_{file_obj.name}"

            sb = get_client()
            bucket = os.environ.get("SUPABASE_BUCKET", "photos")

            try:
                content = file_obj.read()

                sb.storage.from_(bucket).upload(
                    path=filename,
                    file=content,
                    file_options={
                        "content-type": file_obj.content_type or "application/octet-stream",
                        "upsert": "true",
                    },
                )

                public_url_res = sb.storage.from_(bucket).get_public_url(filename)
                public_url = public_url_res if isinstance(public_url_res, str) else public_url_res.get("publicUrl")

                Photo.objects.create(
                    name=form.cleaned_data["name"],
                    image_url=public_url or "",
                )
                return redirect("photo_list")

            except Exception as e:
                logger.exception("Supabase upload failed")
                # ideiglenesen kiírjuk a hibát a böngészőnek is
                return render(request, "album/photo_form.html", {"form": form, "error": str(e)})

    else:
        form = PhotoForm()
    return render(request, "album/photo_form.html", {"form": form})

def photo_delete(request, pk):
    photo = get_object_or_404(Photo, pk=pk)
    if request.method == "POST":
        photo.delete()
        return redirect("photo_list")
    return render(request, "album/photo_delete.html", {"photo": photo})