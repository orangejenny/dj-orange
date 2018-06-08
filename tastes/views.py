import random

from django.http import JsonResponse, HttpResponse
from django.template import loader
from django.views.decorators.http import require_GET

from tastes.models import Album, Song, SongTag, Track


@require_GET
def index(request):
    colors = ['red', 'orange', 'yellow', 'olive', 'green', 'teal', 'blue', 'violet', 'purple', 'pink', 'brown', 'grey', 'black']
    template = loader.get_template('tastes/songs.html')
    context = {
        'color': random.choice(colors),
    }
    return HttpResponse(template.render(context, request))

@require_GET
def song_list(request):
    page = int(request.GET['page'])
    songs_per_page = 50
    start_index = (page - 1) * songs_per_page
    songs = Song.list()
    count = len(songs)
    songs = songs[start_index:(start_index + songs_per_page)]
    context = {
        'count': count,
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
    }
    return JsonResponse(context)

@require_GET
def export(request):
    filenames = ["/Volumes/Flavors/{}".format(s.filename) for s in Song.list()]
    response = HttpResponse("\n".join(filenames))
    response['Content-Disposition'] = 'attachment; filename="{}.m3u"'.format("flavors")
    return response
