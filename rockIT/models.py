import os
from django.db import models

# Create your models here.
from django.contrib.auth.models import User

from rocknroll.settings import MEDIA_ROOT

def user_directory_path(self, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'user_{0}/{1}'.format(self.creator.username, filename)

def user_directory_path_file(self, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'user_{0}/{1}'.format(self.publisher, filename)


class Profile(models.Model):
    user = models.OneToOneField(User , on_delete=models.CASCADE)
    auth_token = models.CharField(max_length=100, null=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username
    


class Album(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=2000, null=True)
    thumbnail = models.FileField(upload_to=user_directory_path)
    genre = models.CharField(max_length=50, null=True) #Category
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='albums')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def delete_media(self):
        os.remove(path=MEDIA_ROOT+'/'+str(self.thumbnail))
        


class Podcast(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=40, null=False)
    description = models.CharField(max_length=500, null=True)
    file = models.FileField(upload_to=user_directory_path_file)
    publisher = models.CharField(max_length=50)
    speaker = models.CharField(max_length=50, null=False)
    views = models.IntegerField(default=0)
    album_id = models.IntegerField(null=True)
    thumbnail = models.FileField(upload_to=user_directory_path_file)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title +' from '+ str(self.album_id)

    def delete_media(self):
        os.remove(path=MEDIA_ROOT+'/'+str(self.file))



class Favourites(models.Model):
    username = models.CharField(max_length=150)
    favourites = models.TextField(default="")

    def __str__(self):
        return "Favourites of " + self.username
    

#This table stores users' history along with paused timestamp
class History(models.Model):
    username = models.CharField(max_length=150)
    podcast_id=models.IntegerField(null=False)
    podcast_timestamp=models.CharField(max_length=50,null=True)

    def __str__(self):
        return self.username + " listened to " + str(self.podcast_id) + " until " + self.podcast_timestamp