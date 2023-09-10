from django.urls import path

from kilo.views import days, history, recent

urlpatterns = [
    path('', days, name='days'),
    path('history/', history, name='history'),
    path('recent/', recent, name='recent'),
]
