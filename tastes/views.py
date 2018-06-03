import random

from django.http import HttpResponse
from django.template import loader
from django.views.decorators.http import require_GET

from tastes.models import Album, Song, SongTag, Track


@require_GET
def index(request):
    colors = ['red', 'orange', 'yellow', 'olive', 'green', 'teal', 'blue', 'violet', 'purple', 'pink', 'brown', 'grey', 'black']
    template = loader.get_template('tastes/songs.html')
    songs = Song.list()
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
        } for s in songs],
        'color': random.choice(colors),
        'count': len(songs),
    }
    return HttpResponse(template.render(context, request))

@require_GET
def export(request):
    filenames = ["/Volumes/Flavors/{}".format(s.filename) for s in Song.list()]
    response = HttpResponse("\n".join(filenames))
    response['Content-Disposition'] = 'attachment; filename="{}.m3u"'.format("flavors")
    return response
