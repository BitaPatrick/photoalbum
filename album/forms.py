from django import forms
from .models import Photo

class PhotoForm(forms.ModelForm):
    image = forms.FileField(required=True)

    class Meta:
        model = Photo
        fields = ["name", "image"]