from django.urls import path

from rhyme.views import (
    albums,
    album_list,
    album_export,
    artist_select2,
    csv_songs,
    csv_tags,
    index,
    json_artists,
    json_colors,
    matrix,
    matrix_json,
    network,
    network_json,
    playlist,
    playlist_export,
    playlist_select2,
    plex_in,
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
    path('csv/song', csv_songs, name='csv_songs'),
    path('csv/tag', csv_tags, name='csv_tags'),
    path('json/artists', json_artists, name='json_artists'),
    path('json/colors', json_colors, name='json_colors'),
    path('playlist/', playlist, name='playlist'),
    path('playlist/export/', playlist_export, name='playlist_export'),
    path('playlist/select2/', playlist_select2, name='playlist_select2'),
    path('plex/in/<slug:api_key>/', plex_in, name='plex_in'),
    path('songs/list/', song_list, name='song_list'),
    path('songs/update/', song_update, name='song_update'),
    path('songs/export/', song_export, name='song_export'),
    path('stats/matrix/', matrix, name='matrix'),
    path('stats/matrix/json/', matrix_json, name='matrix_json'),
    path('stats/network/', network, name='network'),
    path('stats/network/json/', network_json, name='network_json'),
    path('tags/select2/', tag_select2, name='tag_select2'),
]
