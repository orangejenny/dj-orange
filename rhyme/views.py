import random

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.template import loader
from django.views.decorators.http import require_GET

from rhyme.models import Album, Song, SongTag, Track


@require_GET
@login_required
def index(request):
    colors = ['red', 'orange', 'yellow', 'olive', 'green', 'teal', 'blue', 'violet', 'purple', 'pink', 'brown', 'grey', 'black']
    template = loader.get_template('rhyme/songs.html')
    context = {
        'color': random.choice(colors),
    }
    return HttpResponse(template.render(context, request))

@require_GET
@login_required
def song_list(request):
    page = int(request.GET['page'])
    filters = request.GET['filters']
    songs_per_page = 20
    start_index = (page - 1) * songs_per_page
    songs = Song.list(filters)
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
@login_required
def albums(request):
    template = loader.get_template('rhyme/albums.html')
    context = {
        'albums': [
            {
                "acronym": album.acronym,
                "acronym_size": album.acronym_size,
                **vars(album),
            } for album in Album.list().order_by('-date_acquired')
        ],
    }
    return HttpResponse(template.render(context, request))
    

@require_GET
@login_required
def export(request):
    filenames = ["/Volumes/Flavors/{}".format(s.filename) for s in Song.list()]
    response = HttpResponse("\n".join(filenames))
    response['Content-Disposition'] = 'attachment; filename="{}.m3u"'.format("flavors")
    return response


@require_GET
@login_required
def export_album(request, album_id):
    album = Album.objects.get(id=album_id)
    filenames = [
        "/Volumes/Flavors/{}".format(t.song.filename)
        for t in album.track_set.all()
    ]
    response = HttpResponse("\n".join(filenames))
    response['Content-Disposition'] = 'attachment; filename="{}.m3u"'.format(album.name)
    return response
