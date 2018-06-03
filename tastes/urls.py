from django.urls import path

from tastes.views import export, index

urlpatterns = [
    path('', index, name='index'),
    path('export/', export, name='export'),
]
