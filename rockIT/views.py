from rockIT.forms import NewAlbum, NewPodcast
from rockIT.models import Profile
from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from django.contrib import messages
from .models import *
import uuid
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth import authenticate,login
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django import forms
from django.http import HttpResponse, JsonResponse
# Create your views here.

@login_required
def home(request):
    podcasts = Podcast.objects.all()
    ordered = Podcast.objects.order_by('-views')
    return render(request , 'home.html', {"username": request.user.username, "podcasts": podcasts, "ordered":ordered })

def search_tags(request):
    search_query = request.GET.get('q', '').lower()
    matching_tags = Podcast.objects.filter(title__icontains=search_query)
    tags_data = [{'id': tag.id, 'name': tag.title, 'thumbnail': str(tag.thumbnail)} for tag in matching_tags]
    tags_data=tags_data[:20]
    return JsonResponse(tags_data, safe=False)


def login_attempt(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user_obj = User.objects.filter(username = username).first()
        if user_obj is None:
            messages.success(request, 'User not found')
            return redirect('/accounts/login')
        
        profile_obj = Profile.objects.filter(user = user_obj ).first()
        if(profile_obj == None):
            messages.success(request, 'User not found')
            return redirect('/accounts/login')

        if not profile_obj.is_verified:
            messages.success(request, 'Profile is not verified check your mail')
            return redirect('/accounts/login')

        user = authenticate(username = username , password = password)
        if user is None:
            messages.success(request, 'Wrong password')
            return redirect('/accounts/login')
        
        login(request , user)
        return redirect('/')

    return render(request , 'login.html')


def register_attempt(request):
    if request.method == 'POST':
        emailValidate = forms.EmailField()
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            emailValidate.clean(email)
            if User.objects.filter(username = username).first():
                messages.success(request, 'Username is taken')
                return redirect('/register')

            if User.objects.filter(email = email).first():
                messages.success(request, 'Email is taken')
                return redirect('/register')
            
            user_obj = User(username = username , email = email)
            user_obj.set_password(password)
            user_obj.save()
            auth_token = str(uuid.uuid4())
            profile_obj = Profile.objects.create(user = user_obj , auth_token = auth_token)
            profile_obj.save()
            send_mail_after_registration(email , auth_token)
            return redirect('/token')
        except forms.ValidationError as e:
            messages.success(request, 'Enter a valid email address')
            return redirect("/register")
        except Exception as e:
            print(e)


    return render(request , 'register.html')

def success(request):
    return render(request , 'success.html')


def token_send(request):
    return render(request , 'token_send.html')


def verify(request, auth_token):
    try:
        profile_obj = Profile.objects.filter(auth_token = auth_token).first()
        if profile_obj:
            if profile_obj.is_verified:
                if(profile_obj.type == None):
                    return redirect('/')
                messages.success(request, 'Your account is already verified')
                return redirect('/accounts/login')
            profile_obj.is_verified = True
            profile_obj.auth_token = None
            profile_obj.save()
            messages.success(request, 'Your account has been verified')
            return redirect('/')
        else:
            return redirect('/error')
    except Exception as e:
        print(e)
        return redirect('/')


def error_page(request):
    return  render(request , 'error.html')

def logout_view(request):
    logout(request)
    return redirect('home')

def forgot(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        user_obj = User.objects.filter(email = email).first()
        if user_obj is None:
            messages.success(request, 'User not found')
            return redirect('/forgot')
        
        profile_obj = Profile.objects.filter(user = user_obj ).first()
        auth_token = str(uuid.uuid4())
        profile_obj.auth_token = auth_token
        profile_obj.save()
        send_mail_after_registration(email , auth_token, "reset")
        messages.success(request, 'A reset link has been sent to your registered mail')

    return  render(request , 'forgot.html')


def reset(request, auth_token):
    if request.method == 'POST':
        profile_obj = Profile.objects.filter(auth_token = auth_token ).first()
        new_password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        if(new_password != confirm_password):
            messages.success(request, 'Confirmation password did not match the new password')
            return redirect(f'/reset/{auth_token}')
        user_obj = profile_obj.user
        user_obj.set_password(new_password)
        user_obj.save()
        profile_obj.auth_token = None
        profile_obj.save()
        return redirect("/")

    return render(request , 'reset.html')



def send_mail_after_registration(email , token, type="verify"):
    subject = 'Your accounts need to be verified'
    message = f'Hi click on this link to verify your account http://dheeraj2003.pythonanywhere.com/verify/{token}'
    if(type == "reset"):
        subject = "Reset Link for RockIT"
        message = f'Hi click on this link to reset your password http://dheeraj2003.pythonanywhere.com/reset/{token}'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message , email_from ,recipient_list)



#Helper functions to check if the file is video/not
def isVideo(path):
    extension = str(path).split(".")[-1]
    if(extension.lower() in ['mp4', 'mov', 'mpeg4', 'webm', 'ogg', 'wav', 'hls', 'mpeg-4']):
        return True
    return False

#Helper functions to check if the file is audio or not
def isAudio(path):
    extension = str(path).split(".")[-1]
    if(extension.lower() in ['mp3', 'aap']):
        return True
    return False


@login_required
def upload_podcast(request):
    if request.method == 'POST':
        form = NewPodcast(request.POST, request.FILES)
        if form.is_valid():
            # form.save(commit='False')
            podcast = Podcast.objects.create(
                title = form.cleaned_data.get('title'),
                description = form.cleaned_data.get('description'),
                publisher = request.user.username,
                speaker = form.cleaned_data.get('speaker'),
                file = form.cleaned_data.get('file'),
                thumbnail = form.cleaned_data.get('thumbnail'),
                album_id = 100 #form.cleaned_data.get('album_id')
            )
            return redirect('/')

    else:
        form = NewPodcast()
        return render(request, 'upload.html', {'form':form})
    

@login_required
def get_all_my_albums(request):
    my_albums = Album.objects.filter(creator = request.user)
    return render(request, "my_albums.html", {"my_albums": my_albums, "username": request.user.username})

@login_required
def get_my_album(request, album_id):
    podcasts = Podcast.objects.filter(album_id = album_id)
    album = Album.objects.filter(id = album_id).first()
    return render(request, "my_album_podcasts.html", {"podcasts": podcasts, "album": album ,"username": request.user.username})


@login_required
def upload_podcast_to_album(request, album_id):
    if request.method == 'POST':
        form = NewPodcast(request.POST, request.FILES)
        if form.is_valid():
            # form.save(commit='False')
            podcast = Podcast.objects.create(
                title = form.cleaned_data.get('title'),
                description = form.cleaned_data.get('description'),
                publisher = request.user.username,
                speaker = form.cleaned_data.get('speaker'),
                file = form.cleaned_data.get('file'),
                thumbnail = form.cleaned_data.get('thumbnail'),
                album_id = album_id
            )
            return redirect('/uploads/albums/' + str(album_id))
    else:
        form = NewPodcast()
        return render(request, 'upload.html', {'form':form})
    

@login_required
def create_album(request):
    if request.method == 'POST':
        form = NewAlbum(request.POST, request.FILES)
        if form.is_valid():
            print("Inside post")
            album = Album.objects.create(
                title = form.cleaned_data.get('title'),
                description = form.cleaned_data.get('description'),
                creator = request.user,
                genre = form.cleaned_data.get('genre'),
                thumbnail = form.cleaned_data.get('thumbnail')
            )
            return redirect('/uploads/albums')
        else:
            return redirect("/uploads/albums")
    
    form = NewAlbum()
    return render(request, 'create_album.html', {'form':form})


def get_podcast(request, id):
    podcast = Podcast.objects.filter(id = id).first()
    podcast.views = podcast.views + 1
    podcast.save()
    favourites = Favourites.objects.filter(username = request.user.username).first()
    fav_exist = True
    fill = "none"
    if(favourites == None):
        fav_exist = False
    else:
        fav_id_set = set(map(int, favourites.favourites.split()))
        if(podcast.id in fav_id_set):
            fill = "red"
    related_podcasts = Podcast.objects.filter(album_id = podcast.album_id)
    type = "none"
    if(isAudio(podcast.file)):
        type = "audio"
    elif(isVideo(podcast.file)):
        type = "video"
        return render(request, "video_podcast.html", {"podcast": podcast, "type": type, "related_podcasts": related_podcasts, "fill":fill})
    
    return render(request, "podcast.html", {"podcast": podcast, "type": type, "related_podcasts": related_podcasts, "fill":fill})



def delete_podcast(request, id):
    podcast = Podcast.objects.filter(id = id).first()
    album_id=podcast.album_id
    podcast.delete_media()
    podcast.delete()
    return redirect('/uploads/albums/'+str(album_id))



def update_podcast(request, id):
    podcast = Podcast.objects.filter(id = id).first()
    album_id=podcast.album_id
    if request.method == 'POST':
        podcast.title=request.POST['title']
        podcast.description=request.POST['description']
        podcast.speaker=request.POST['speaker']
        podcast.save()
        return redirect('/uploads/albums/' + str(album_id))
    
    return render(request,"update_podcast.html", {"podcast": podcast})



def set_favourite(request, id):
    favourites = Favourites.objects.filter(username = request.user.username).first()
    if(favourites == None):
        favourites = Favourites.objects.create(username = request.user.username, favourites = str(id))
        return HttpResponse(status=200)
    fav_ids = set(favourites.favourites.split())
    fav_ids.add(id)
    favourites.favourites = " ".join(fav_ids)
    favourites.save()
    print(favourites.favourites)
    return HttpResponse(status=200)


def get_favourites(request):
    favourites = Favourites.objects.filter(username = request.user.username).first()
    fav_exist = True
    podcasts = []
    if(favourites == None):
        fav_exist = False
        return render(request, "favourites.html", {"fav_exist": fav_exist, "favourites": [], "podcasts":podcasts })
    else:
        podcasts = Podcast.objects.filter(id__in = list(map(int, favourites.favourites.split())))
    return render(request, "favourites.html", {"fav_exist": fav_exist, "favourites": favourites.favourites.split(), "podcasts":podcasts })


def genre(request):
    return render(request, "genre.html")


def genre_category(request, category):
    albums = Album.objects.filter(genre__contains = category)
    return render(request, "category.html", {"podcasts": albums, "genre": category})

def getPodcastHistory(request,id):
    hist=History.objects.filter(username = request.user.username,podcast_id=id).first()
    # print(hist)
    if not (hist):
        tags_data = {'time': 0}
        return JsonResponse(tags_data)
    else:
        tags_data = {'time': hist.podcast_timestamp}
        return JsonResponse(tags_data)
    
def setPodcastHistory(request,id,time):
    hist=History.objects.filter(username = request.user.username, podcast_id=id).first()
    if not (hist):
        hist=History.objects.create(username = request.user.username, podcast_id=id,podcast_timestamp=time)
        tags_data = {'time': time}
        return JsonResponse(tags_data)
    else:
        hist.podcast_timestamp=time
        hist.save()
        tags_data = {'time': hist.podcast_timestamp}
        return JsonResponse(tags_data)