
from django.contrib import admin
from django.urls import path
from .views import *


urlpatterns = [
    path('' ,  home  , name="home"),
    path('register' , register_attempt , name="register_attempt"),
    path('accounts/login/' , login_attempt , name="login_attempt"),
    path('token' , token_send , name="token_send"),
    path('success' , success , name='success'),
    path('verify/<auth_token>' , verify , name="verify"),
    path('error' , error_page , name="error"),
    path('forgot' , forgot , name="forgot"),
    path('reset/<auth_token>' , reset , name="reset"),
    path("search_tags/", search_tags, name="search_tags"),
    path("logout/", logout_view, name="logout_view"),

    path('podcast/new', upload_podcast, name="upload_podcast"),
    path('uploads/albums', get_all_my_albums, name="get_my_albums"),
    path('uploads/albums/<album_id>', get_my_album, name="get_my_album"),
    path('uploads/albums/<album_id>/new', upload_podcast_to_album, name="add_podcast_to_album"),
    path('uploads/new/albums', create_album, name="add_podcast_to_album"),
    path('podcast/<id>', get_podcast, name="get_podcast"),
    path('uploads/deletepodcast/<id>',delete_podcast,name='deletepodcast'),
    path('uploads/updatepodcast/<id>',update_podcast,name='updatepodcast'),
    path('favourites/<id>' , set_favourite , name="set_favourite"),
    path('favourites' , get_favourites , name="get_favourite"),
    path('genre', genre, name="genre"),
    path('genre/<category>', genre_category, name="genre_category"),
    path('history/get/<id>',getPodcastHistory,name="gethistory"),
    path('history/set/<id>/<time>',setPodcastHistory,name="gethistory")

]