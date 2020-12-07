from django.urls import path

from kilo.views import days, days_erging, days_running, panel

urlpatterns = [
    path('', days, name='days'),
    path('erging/', days_erging, name='days_erging'),
    path('running/', days_running, name='days_running'),
    path('panel/', panel, name='panel'),
]
