from django.urls import path

from miles.views import days

urlpatterns = [
    path('', days, name='days'),
]
