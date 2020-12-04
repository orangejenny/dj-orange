from django.urls import path

from miles.views import days, panel

urlpatterns = [
    path('', days, name='days'),
    path('panel/', panel, name='panel'),
]
