from django.urls import path

from rhyme.views import albums, export, index, song_list

urlpatterns = [
    path('', index, name='index'),
    path('albums/', albums, name='albums'),
    path('songs/list/', song_list, name='song_list'),
    path('export/', export, name='export'),
]
