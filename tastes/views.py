from django.http import HttpResponse
from django.template import loader

from tastes.models import Album, Song, SongTag, Track


def index(request):
    template = loader.get_template('tastes/songs.html')
    context = {
        'songs': [{
            'name': s.name,
            'artist': s.artist,
            'rating': s.rating or '',
            'energy': s.energy or '',
            'mood': s.mood or '',
            'starred': s.starred,
            'albums': s.albums,
            'tags': s.tags,
        } for s in Song.objects.all()[:10]],
    }
    return HttpResponse(template.render(context, request))
