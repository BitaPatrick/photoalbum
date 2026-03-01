from django.db import models


class Photo(models.Model):
    name = models.CharField(max_length=40)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    # Supabase Storage objektum útvonal (pl. "photos/uuid_filename.png")
    storage_path = models.CharField(max_length=500)

    # Publikus URL (vagy signed URL, ha nem public bucket)
    image_url = models.URLField(max_length=1000)

    def __str__(self):
        return self.name
