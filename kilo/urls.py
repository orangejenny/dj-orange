from django.urls import path

from kilo.views import base, frequency, history, pace, recent, stats

urlpatterns = [
    path('', base, name='base'),
    path('frequency/', frequency, name='frequency'),
    path('history/', history, name='history'),
    path('pace/', pace, name='pace'),
    path('recent/', recent, name='recent'),
    path('stats/', stats, name='stats'),
]
