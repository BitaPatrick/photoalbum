from django import forms

class PhotoForm(forms.Form):
    name = forms.CharField(max_length=200)
    image = forms.ImageField()