from django.urls import path

from kilo.views import base, history, recent, stats

urlpatterns = [
    path('', base, name='base'),
    path('history/', history, name='history'),
    path('recent/', recent, name='recent'),
    path('stats/', stats, name='stats'),
]
