from datetime import datetime
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
    albums = []
    for album in Album.list().order_by('-date_acquired'):
        ratings = [s.rating for s in album.songs if s.rating]
        energies = [s.energy for s in album.songs if s.energy]
        moods = [s.mood for s in album.songs if s.mood]
        if album.songs:
            completion = sum([1 for s in album.songs if s.rating])
            completion += sum([1 for s in album.songs if s.energy])
            completion += sum([1 for s in album.songs if s.mood])
            completion = completion * 100 / (3 * len(album.songs))
        else:
            completion = 0
        albums.append({
            "acronym": album.acronym,
            "acronym_size": album.acronym_size,
            "artist": album.artist,
            "cover_art_filename": album.cover_art_filename,
            "export_html": album.export_html,
            "completion_text": "({}% complete)".format(round(completion)),
            "stats": {
                # TODO: DRY up? Move into Album model? Also move completion into Album
                "rating": {
                    "min": min(ratings) if ratings else None,
                    "avg": sum(ratings) / len(ratings) if ratings else None,
                    "max": max(ratings) if ratings else None,
                },
                "energy": {
                    "min": min(energies) if energies else None,
                    "avg": sum(energies) / len(energies) if energies else None,
                    "max": max(energies) if energies else None,
                },
                "mood": {
                    "min": min(moods) if moods else None,
                    "avg": sum(moods) / len(moods) if moods else None,
                    "max": max(moods) if moods else None,
                },
            },
            **vars(album),
        })
    context = {
        'albums': albums,
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
    album.last_export = datetime.now()
    album.export_count = album.export_count + 1
    album.save()

    filenames = [
        "/Volumes/Flavors/{}".format(song.filename)
        for song in album.songs
    ]
    response = HttpResponse("\n".join(filenames))
    response['Content-Disposition'] = 'attachment; filename="{}.m3u"'.format(album.name)
    return response
