from django.urls import path

from rhyme.views import (
    albums,
    album_list,
    export,
    export_album,
    index,
    song_list,
)

urlpatterns = [
    path('', index, name='index'),
    path('albums/', albums, name='albums'),
    path('albums/list/', album_list, name='album_list'),
    path('songs/list/', song_list, name='song_list'),
    path('export/', export, name='export'),
    path('export/album/<int:album_id>/', export_album, name='export_album'),
]
