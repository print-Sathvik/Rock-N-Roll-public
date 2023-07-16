from django.contrib.auth.models import User
from django import forms
from django.contrib.auth.forms import UserCreationForm

from rockIT.models import Album, Podcast

class NewPodcast(forms.ModelForm):
    title = forms.CharField(required='True')
    description = forms.CharField(required='True')
    speaker = forms.CharField(required='True')
    file = forms.FileField(required='True')
    thumbnail = forms.FileField(required='True')

    class Meta:
        model = Podcast
        fields = ('title', 'description', 'speaker', 'file', 'thumbnail')


class NewAlbum(forms.ModelForm):
    title = forms.CharField(required='True')
    description = forms.CharField(required='True')
    genre = forms.CharField(required='True')
    thumbnail = forms.FileField(required='True')

    class Meta:
        model = Album
        fields = ('title', 'description', 'genre', 'thumbnail')