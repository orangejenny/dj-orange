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
from rhyme.models import Album, Artist, Color, Song, Tag, Track


def _rhyme_context():
    from rhyme.urls import urlpatterns
    return {
        "RHYME_EXPORT_CONFIGS": settings.RHYME_EXPORT_CONFIGS,
        "RHYME_GENRES": Artist.all_genres(),
        "RHYME_URLS": {
            p.name: reverse(p.name) for p in urlpatterns
        },
    }


@require_GET
@login_required
def index(request):
    template = loader.get_template('rhyme/songs.html')
    context = {
        **_rhyme_context(),
    }
    return HttpResponse(template.render(context, request))


@require_GET
@login_required
def song_list(request):
    omni_filter = request.GET.get('omni_filter', '')
    if request.GET.get("album_id"):
        album = Album.objects.get(id=request.GET.get("album_id"))
        tracks = [(track.disc, track.ordinal, track.song)
                  for track in album.tracks]
        if album.disc_set.count():
            disc_names = [disc.name for disc in album.disc_set.all()]
        else:
            disc_names = [f"Disc {index + 1}" for index in range(max([disc for disc, ordinal, song in tracks]))]
        count = len(tracks)
        more = False
    else:
        page = int(request.GET.get('page', 1))
        filters = request.GET.get('song_filters')
        songs_per_page = 20
        songs = Song.list(filters, omni_filter)
        count = songs.count()
        paginator = Paginator(songs, songs_per_page)
        more = paginator.num_pages > page
        tracks = [(None, None, song) for song in paginator.get_page(page)]
        disc_names = []

    context = {
        'count': count,
        'omni_filter': omni_filter,
        'more': more,
        'items': [{
            'id': song.id,
            'name': song.name,
            'artist': song.artist.name,
            'rating': song.rating or '',
            'energy': song.energy or '',
            'mood': song.mood or '',
            'starred': song.starred,
            'year': song.year,
            'albums': ", ".join(song.albums),
            'tags': song.tags(),
            'disc_number': disc_number,
            'track_number': track_number,
        } for disc_number, track_number, song in tracks],
        'disc_names': disc_names,
    }
    return JsonResponse(context)


@require_POST
@login_required
def song_update(request):
    song = Song.objects.get(id=request.POST.get("id"))
    field = request.POST.get("field")
    value = request.POST.get("value")

    if field == 'tags':
        value = re.sub(r'\s+', ' ', value.strip())   # normalize whitespace
        song.tag_set.clear()
        for name in set(value.split(" ")):
            (tag, tag_created) = Tag.objects.get_or_create(name=name)
            song.tag_set.add(tag)
            if tag_created:
                tag.save()
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
    omni_filter = request.GET.get('omni_filter', '')
    album_filters = request.GET.get('album_filters')
    song_filters = request.GET.get('song_filters')
    albums_per_page = 25
    album_queryset = Album.list(album_filters, song_filters, omni_filter)
    paginator = Paginator(album_queryset.order_by('-date_acquired'), albums_per_page)
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
            "id": album.id,
            "name": album.name,
            "date_acquired": _format_date(album.date_acquired),
            "export_count": album.export_count,
            "last_export": _format_date(album.last_export),
            "starred": album.starred,
        })
    context = {
        'count': album_queryset.count(),
        'omni_filter': omni_filter,
        'more': paginator.num_pages > page,
        'items': albums,
    }
    return JsonResponse(context)


def _format_date(date):
    if not date:
        return ""
    return date.strftime("%b %d, %Y")


@require_GET
@login_required
def playlist(request):
    template = loader.get_template('rhyme/playlist.html')
    context = {
        **_rhyme_context(),
    }
    return HttpResponse(template.render(context, request))


@require_GET
@login_required
def artist_select2(request):
    return _select2_list(request, Artist.objects)


@require_GET
@login_required
def tag_select2(request):
    return _select2_list(request, Tag.objects)


def _select2_list(request, objects):
    query = request.GET.get("term")
    if query:
        objects = objects.filter(name__icontains=query)
    else:
        objects = objects.all()
    names = sorted(objects.values_list('name', flat=True))
    return JsonResponse({
        "items": [{
            "text": name,
            "id": name,
        } for name in names],
    })


@require_GET
@login_required
def album_export(request):
    album_id = request.GET.get('album_id')
    if album_id:
        album = Album.objects.get(id=album_id)
        album.audit_export()
        return _m3u_response(request, album.songs)

    album_filters = request.GET.get('album_filters')
    song_filters = request.GET.get('song_filters')
    omni_filter = request.GET.get('omni_filter')
    songs = []
    # TODO: use tracks to do this, either with an Album.list_songs method or by adding album_filters to Song.list
    for album in Album.list(album_filters, song_filters, omni_filter):
        songs += album.songs
        album.audit_export()
    return _m3u_response(request, songs)


@require_GET
@login_required
def playlist_export(request):
    album_filters = request.GET.get('album_filters')    # TODO: use these
    song_filters = request.GET.get('song_filters')
    filtered_songs = Song.list(song_filters)

    # TODO: DRYer with command
    attrs = ["rating", "energy", "mood"]
    start_values = {}
    end_values = {}
    ranges = {}
    for attr in attrs:
        start = request.GET.get(attr + "_start")
        end = request.GET.get(attr + "_end")
        if start and end:
            start_values[attr] = int(start)
            end_values[attr] = int(end)
            ranges[attr] = end_values[attr] - start_values[attr]

    # TODO: DRYer with command
    total_time = 60 * 60
    accumulated_time = 0
    songs = set()
    stop = False
    while not stop and accumulated_time < total_time:
        kwargs = {}
        for attr in attrs:
            if attr not in ranges:
                continue

            ratio = accumulated_time / total_time
            filter_value = round(start_values[attr] + ratio * ranges[attr])
            kwargs[attr] = filter_value
        candidates = filtered_songs.filter(time__isnull=False, **kwargs).order_by('?')
        candidates = candidates.exclude(id__in=[song.id for song in songs])
        song = candidates.first()
        if song:
            songs.add(song)
            accumulated_time += song.time
        else:
            stop = True

    return _m3u_response(request, songs)    # TODO: name playlist


@require_GET
@login_required
def song_export(request):
    song_filters = request.GET.get('song_filters')
    omni_filter = request.GET.get('omni_filter')
    return _m3u_response(request, Song.list(song_filters, omni_filter))


def _m3u_response(request, songs):
    for song in songs:
        song.audit_export()     # TODO: move to filenames

    response = HttpResponse("\n".join(filenames(request.GET.get("config"), songs)))
    response['Content-Disposition'] = 'attachment; filename="{}.m3u"'.format(request.GET.get("filename", "rhyme"))
    return response


def filenames(config_name, songs):       # TODO: move to models
    try:
        config = [c for c in settings.RHYME_EXPORT_CONFIGS if c["name"] == config_name][0]
    except IndexError:
        raise ExportConfigNotFoundException(f"Could not find {config_name}")

    return [config["prefix"] + s.filename for s in songs]
