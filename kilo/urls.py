from django.urls import path

from kilo.views import (
    add_workout,
    copy,
    base,
    delete_workout,
    erging,
    frequency,
    history,
    lifting,
    long_runs,
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
    path('activity/erging/', erging, name='erging'),
    path('activity/lifting/', lifting, name='lifting'),
    path('activity/long_runs/', long_runs, name='long_runs'),
    path('pace/', pace, name='pace'),
    path('recent/', recent, name='recent'),
    path('stats/', stats, name='stats'),
    path('copy/', copy, name='copy'),
    path('update/', update, name='update'),
    path('workout/add/', add_workout, name='add_workout'),
    path('workout/delete/', delete_workout, name='delete_workout'),
    path('workout/update/', update_workout, name='update_workout'),
]
