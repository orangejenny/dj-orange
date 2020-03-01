from django.urls import path

from rhyme.views import (
    albums,
    album_list,
    album_export,
    artist_select2,
    index,
    playlist,
    playlist_export,
    song_list,
    song_update,
    song_export,
    tag_select2,
)

urlpatterns = [
    path('', index, name='index'),
    path('albums/', albums, name='albums'),
    path('albums/list/', album_list, name='album_list'),
    path('albums/export/', album_export, name='album_export'),
    path('artists/select2/', artist_select2, name='artist_select2'),
    path('playlist/', playlist, name='playlist'),
    path('playlist/export/', playlist_export, name='playlist_export'),
    path('songs/list/', song_list, name='song_list'),
    path('songs/update/', song_update, name='song_update'),
    path('songs/export/', song_export, name='song_export'),
    path('tags/select2/', tag_select2, name='tag_select2'),
]
