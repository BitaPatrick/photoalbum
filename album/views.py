import os, uuid
from django.shortcuts import render, redirect, get_object_or_404
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

def photo_upload(request):
    if request.method == "POST":
        form = PhotoForm(request.POST, request.FILES)
        if form.is_valid():
            client = get_client()
            bucket = os.environ.get("SUPABASE_BUCKET", "photos")

            f = form.cleaned_data["image"]
            ext = os.path.splitext(f.name)[1].lower() or ".jpg"
            filename = f"{uuid.uuid4()}{ext}"

            # ajánlott: mappába rakni
            path = f"uploads/{filename}"

            data = f.read()
            content_type = getattr(f, "content_type", "application/octet-stream")

            res = client.storage.from_(bucket).upload(
                path,
                data,
                {"content-type": content_type, "upsert": True},
            )

            # Ha hibát ad vissza, dobjunk értelmes üzenetet
            # (a supabase lib néha dict-et ad, néha objektumot – ezért óvatosan)
            if isinstance(res, dict) and res.get("error"):
                return render(request, "album/photo_form.html", {"form": form, "error": str(res)})

            public_url = client.storage.from_(bucket).get_public_url(path)

            Photo.objects.create(
                name=form.cleaned_data["name"],
                storage_path=path,
                image_url=public_url,
            )
            return redirect("photo_list")
    else:
        form = PhotoForm()

    return render(request, "album/photo_form.html", {"form": form})