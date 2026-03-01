from django import forms
from .models import Photo

class PhotoForm(forms.ModelForm):
    
    image = forms.ImageField(required=True)

    class Meta:
        model = Photo
        fields = ["name"] 