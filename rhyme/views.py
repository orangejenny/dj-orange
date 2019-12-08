from datetime import datetime
import random
import re

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse
from django.template import loader
from django.urls import reverse
from django.views.decorators.http import require_GET, require_POST

from rhyme.exceptions import ExportConfigNotFoundException
from rhyme.models import Album, Color, Song, SongTag, Tag, Track


def _rhyme_context():
    return {
        "RHYME_EXPORT_CONFIGS": settings.RHYME_EXPORT_CONFIGS,
    }


@require_GET
@login_required
def index(request):
    colors = ['red', 'orange', 'yellow', 'olive', 'green', 'teal', 'blue', 'violet', 'purple', 'pink', 'brown', 'grey', 'black']
    template = loader.get_template('rhyme/songs.html')
    context = {
        'color': random.choice(colors),
        **_rhyme_context(),
    }
    return HttpResponse(template.render(context, request))


@require_GET
@login_required
def song_list(request):
    if request.GET.get("album_id"):
        album = Album.objects.get(id=request.GET.get("album_id"))
        songs = album.songs
        pass
    else:
        page = int(request.GET.get('page', 1))
        filters = request.GET.get('filters')
        songs_per_page = 20
        paginator = Paginator(Song.list(filters), songs_per_page)
        songs = paginator.get_page(page)

    count = len(songs)
    context = {
        'count': Song.objects.count(),
        'items': [{
            'id': s.id,
            'name': s.name,
            'artist': s.artist,
            'rating': s.rating or '',
            'energy': s.energy or '',
            'mood': s.mood or '',
            'starred': s.starred,
            'albums': s.albums,
            'tags': s.tags(),
        } for s in songs],
    }
    return JsonResponse(context)


@require_POST
@login_required
def song_update(request):
    song = Song.objects.get(id=request.POST.get("id"))
    field = request.POST.get("field")
    value = request.POST.get("value")

    if field == 'tags':
        # TODO: extract into Song model and add test
        value = re.sub(r'\s+', ' ', value.strip())   # normalize whitespace
        new_tags = set(value.split(" "))

        # Delete old tags
        for song_tag in SongTag.objects.filter(song=song.id):
            if song_tag.tag.name not in new_tags:
                song_tag.delete()

        # Add new tags
        old_tags = set(song.tags())
        for tag in new_tags.difference(old_tags):
            (tag, created) = Tag.objects.get_or_create(name=tag)
            SongTag.objects.create(song=song, tag=tag)
    else:
        setattr(song, field, value)
    song.save()
    return JsonResponse({"success": 1})


@require_GET
@login_required
def albums(request):
    template = loader.get_template('rhyme/albums.html')
    return HttpResponse(template.render(_rhyme_context(), request))


@require_GET
def album_list(request):
    page = int(request.GET['page'])
    albums_per_page = 25        # TODO: this makes the last row not full depending on screen size
    paginator = Paginator(Album.list().order_by('-date_acquired'), albums_per_page)
    albums = []
    for album in paginator.get_page(page):
        color = album.color
        completion = album.completion
        if completion > 0 and completion < 100:
            completion_text = "({}% complete)".format(round(completion))
        else:
            completion_text = ""
        albums.append({
            "acronym": album.acronym,
            "acronym_size": album.acronym_size,
            "artist": album.artist,
            "cover_art_filename": album.cover_art_filename,
            "export_html": album.export_html,
            "color": {                              # TODO: use jsonpickle instead?
                "name": color.name,
                "hex_code": color.hex_code,
                "white_text": color.white_text,
            } if color else {},
            "completion_text": completion_text,
            "stats": album.stats(),
            "tags": album.tags()[:3],
            "id": album.id,
            "name": album.name,
            "date_acquired": _format_date(album.date_acquired),
            "export_count": album.export_count,
            "last_export": _format_date(album.last_export),
            "starred": album.starred,
        })
    context = {
        'count': Album.objects.count(),
        'items': albums,
    }
    return JsonResponse(context)


def _format_date(date):
    if not date:
        return ""
    return date.strftime("%b %d, %Y")


@require_GET
@login_required
def export(request):
    album_id = request.GET.get('album_id')
    if album_id:
        album = Album.objects.get(id=album_id)
        album.last_export = datetime.now()
        album.export_count = album.export_count + 1     # TODO: do songs have a last_export and export_count? should they?
        album.save()
        return _m3u_response(request, album.songs)
    return _m3u_response(request, Song.list())


def _m3u_response(request, songs):
    config_name = request.GET.get("config", None)
    try:
        config = [c for c in settings.RHYME_EXPORT_CONFIGS if c["name"] == config_name][0]
    except IndexError:
        raise ExportConfigNotFound(f"Could not find {config_name}")

    filenames = [config["prefix"] + s.filename for s in songs]
    response = HttpResponse("\n".join(filenames))
    response['Content-Disposition'] = 'attachment; filename="{}.m3u"'.format(request.GET.get("filename", "rhyme"))
    return response
