from django.urls import path

from kilo.views import (
    add_workout,
    copy,
    base,
    delete_workout,
    frequency,
    history,
    pace,
    recent,
    stats,
    update,
    update_workout,
)

urlpatterns = [
    path('', base, name='base'),
    path('frequency/', frequency, name='frequency'),
    path('history/', history, name='history'),
    path('pace/', pace, name='pace'),
    path('recent/', recent, name='recent'),
    path('stats/', stats, name='stats'),
    path('copy/', copy, name='copy'),
    path('update/', update, name='update'),
    path('workout/add/', add_workout, name='add_workout'),
    path('workout/delete/', delete_workout, name='delete_workout'),
    path('workout/update/', update_workout, name='update_workout'),
]
