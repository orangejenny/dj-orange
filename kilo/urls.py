from django.urls import path

from kilo.views import days, panel

urlpatterns = [
    path('', days, name='days'),
    path('panel/', panel, name='panel'),
]
