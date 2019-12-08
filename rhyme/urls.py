from django.urls import path

from rhyme.views import (
    albums,
    album_list,
    export,
    index,
    song_list,
    song_update,
)

urlpatterns = [
    path('', index, name='index'),
    path('albums/', albums, name='albums'),
    path('albums/list/', album_list, name='album_list'),
    path('songs/list/', song_list, name='song_list'),
    path('songs/update/', song_update, name='song_update'),
    path('export/', export, name='export'),
]
