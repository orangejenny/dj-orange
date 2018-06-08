from django.urls import path

from tastes.views import export, index, song_list

urlpatterns = [
    path('', index, name='index'),
    path('songs/list/', song_list, name='song_list'),
    path('export/', export, name='export'),
]
