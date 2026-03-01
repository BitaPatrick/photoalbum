from django.db import models

class Photo(models.Model):
    name = models.CharField(max_length=40)
    image_url = models.URLField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name