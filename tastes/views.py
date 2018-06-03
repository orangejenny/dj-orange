from django.http import HttpResponse
from django.template import loader
from django.views.decorators.http import require_GET

from tastes.models import Album, Song, SongTag, Track


@require_GET
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
        } for s in Song.list()],
    }
    return HttpResponse(template.render(context, request))

@require_GET
def export(request):
    filenames = ["/Volumes/Flavors/{}".format(s.filename) for s in Song.list()]
    response = HttpResponse("\n".join(filenames))
    response['Content-Disposition'] = 'attachment; filename="{}.m3u"'.format("flavors")
    return response
