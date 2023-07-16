from django.contrib import admin

from rockIT.models import *

# Register your models here.
admin.site.register(Profile)
admin.site.register(Album)
admin.site.register(Podcast)
admin.site.register(Favourites)
admin.site.register(History)