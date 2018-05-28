from django.http import HttpResponse
from django.template import loader

from tastes.models import Song, Album, Track


def index(request):
    template = loader.get_template('tastes/songs.html')
    context = {
        'songs': Song.objects.all(),
    }
    return HttpResponse(template.render(context, request))
