from django.db import models

class Photo(models.Model):
    name = models.CharField(max_length=40)

    # régi mező megmarad, de opcionálisra tesszük
    image = models.ImageField(upload_to="photos/", blank=True, null=True)

    # supabase public url ide megy
    image_url = models.URLField(blank=True)

    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name