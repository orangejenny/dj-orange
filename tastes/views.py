from django.http import HttpResponse
from django.template import loader

from tastes.models import Song, Album, Track


def index(request):
    template = loader.get_template('tastes/songs.html')
    context = {
        'songs': [{
            'name': s.name,
            'artist': s.artist,
            'rating': s.rating,
            'energy': s.energy,
            'mood': s.mood,
            'starred': s.starred,
            'tags': s.tags,
        } for s in Song.objects.all()],
    }
    return HttpResponse(template.render(context, request))
