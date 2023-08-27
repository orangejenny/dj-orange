import json
import random
import re

from collections import defaultdict
from datetime import datetime, timezone
from json.decoder import JSONDecodeError

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import connection
from django.db.models import Count
from django.http import JsonResponse, HttpResponse
from django.template import loader
from django.urls import NoReverseMatch, reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from rhyme.exceptions import ExportConfigNotFoundException
from rhyme.models import Album, Artist, Color, Disc, Playlist, PlaylistSong, Song, Tag, Track
from rhyme.plex import create_plex_playlist


def _rhyme_context():
    from rhyme.urls import urlpatterns
    js_urls = {}
    for pattern in urlpatterns:
        try:
            js_urls[pattern.name] = reverse(pattern.name)
        except NoReverseMatch:
            pass
    return {
        "RHYME_EXPORT_CONFIGS": settings.RHYME_EXPORT_CONFIGS,
        "RHYME_GENRES": Artist.all_genres(),
        "RHYME_URLS": js_urls,
    }


@require_GET
@login_required
def index(request):
    template = loader.get_template('rhyme/songs.html')
    context = {
        **_rhyme_context(),
        "has_export": True,
        "model": "song",
        "playlists": [
            {"id": p.id, "name": p.name}
            for p in Playlist.objects.all().order_by("name")
        ],
    }
    return HttpResponse(template.render(context, request))


@require_GET
@login_required
def song_list(request):
    omni_filter = request.GET.get('omni_filter', '')
    context = {
        'omni_filter': omni_filter,
    }

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
        context.update({
            'cover_art_filename': album.cover_art_filename,
        })
        starred_ids = None
    else:
        page = int(request.GET.get('page', 1))
        album_filters = request.GET.get('album_filters')
        song_filters = request.GET.get('song_filters')
        songs_per_page = request.GET.get('songs_per_page', 100)
        songs = Song.list(song_filters=song_filters, album_filters=album_filters, omni_filter=omni_filter)
        count = songs.count()
        paginator = Paginator(songs, songs_per_page)
        more = paginator.num_pages > page
        tracks = [(None, None, song) for song in paginator.get_page(page)]
        disc_names = []
        active_playlist_name = request.GET.get('active_playlist_name') or None
        active_playlist = None
        if active_playlist_name:
            active_playlist = Playlist.objects.filter(name=active_playlist_name).first()
            if active_playlist is None:
                active_playlist = Playlist.empty_playlist()
                active_playlist.name = active_playlist_name
                active_playlist.save()
        starred_ids = [s.id for s in active_playlist.songs] if active_playlist else None

    context.update({
        'count': count,
        'more': more,
        'items': [{
            'id': song.id,
            'name': song.name,
            'artist': song.artist.name,
            'rating': song.rating or '',
            'energy': song.energy or '',
            'mood': song.mood or '',
            'starred': song.id in starred_ids if starred_ids is not None else song.starred,
            'albums': [{'name': album.name, 'id': album.id} for album in song.albums],
            'tags': song.tags(),
            'disc_number': disc_number,
            'track_number': track_number,
        } for disc_number, track_number, song in tracks],
        'disc_names': disc_names,
    })
    return JsonResponse(context)


@require_POST
@login_required
def song_update(request):
    try:
        post_data = json.loads(request.body.decode("utf-8"))
        song = Song.objects.get(id=post_data.get("id"))
        field = post_data.get("field")
        value = post_data.get("value")
        playlist_name = post_data.get("playlist_name") or None
    except JSONDecodeError:
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
    elif field == 'starred' and playlist_name is not None:
        playlist = Playlist.objects.filter(name=playlist_name).first()
        playlist_song = PlaylistSong.objects.filter(playlist_id=playlist.id, song_id=song.id)
        is_natural = song.id in [s.id for s in playlist.natural_songs]

        if value:
            if is_natural:
                if playlist_song:
                    # delete presumable exclusion
                    playlist_song.delete()
            else:
                # add inclusion
                PlaylistSong(playlist_id=playlist.id, song_id=song.id, inclusion=True).save()
        else:
            if is_natural:
                # add exclusion
                PlaylistSong(playlist_id=playlist.id, song_id=song.id, inclusion=False).save()
            else:
                if playlist_song:
                    # delete presumable inclusion
                    playlist_song.delete()
    else:
        setattr(song, field, value)
    song.save()
    return JsonResponse({"success": 1})


@require_GET
@login_required
def albums(request):
    template = loader.get_template('rhyme/albums.html')
    context = {
        **_rhyme_context(),
        "model": "album",
        "has_export": True,
    }
    return HttpResponse(template.render(context, request))


@require_GET
def album_list(request):
    page = int(request.GET['page'])
    omni_filter = request.GET.get('omni_filter', '')
    album_filters = request.GET.get('album_filters')
    song_filters = request.GET.get('song_filters')
    albums_per_page = 25
    album_queryset = Album.list(album_filters, song_filters, omni_filter)
    paginator = Paginator(album_queryset, albums_per_page)
    albums = [album.to_json() for album in paginator.get_page(page)]

    context = {
        'count': album_queryset.count(),
        'omni_filter': omni_filter,
        'more': paginator.num_pages > page,
        'items': albums,
    }
    return JsonResponse(context)


@require_GET
@login_required
def artist_select2(request):
    return _select2_list(request, Artist.objects)


@require_GET
@login_required
def playlist_select2(request):
    return _select2_list(request, Playlist.objects)


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
        return _playlist_response(request, album.songs)

    filter_kwargs = {
        'album_filters': request.GET.get('album_filters'),
        'song_filters': request.GET.get('song_filters'),
        'omni_filter': request.GET.get('omni_filter'),
    }
    songs = []
    for album in Album.list(**filter_kwargs):
        songs += album.songs
        album.audit_export()
    return _playlist_response(request, songs, **filter_kwargs)


@require_GET
@login_required
def song_export(request):
    filter_kwargs = {
        'song_filters': request.GET.get('song_filters'),
        'omni_filter': request.GET.get('omni_filter'),
    }
    return _playlist_response(request, Song.list(**filter_kwargs), **filter_kwargs)


@require_GET
@login_required
def csv_songs(request):
    lines = ["song_id,rating,mood,energy,genre"]
    lines.extend([
        f"{s.id},{s.rating or ''},{s.mood or ''},{s.energy or ''},{s.artist.genre or ''}"
        for s in Song.list()
    ])

    response = HttpResponse("\n".join(lines))
    response['Content-Disposition'] = 'attachment; filename="songs.csv"'
    return response


@require_GET
@login_required
def csv_tags(request):
    category_map = {
        tag.name: tag.category
        for tag in Tag.objects.all()
    }

    lines = ["tag,tag_category,song_id,rating,mood,energy"]
    for s in Song.list():
        for tag in s.tags():
            category = category_map[tag]
            lines.append(f"{tag},{category or ''},{s.id},{s.rating or ''},{s.mood or ''},{s.energy or ''}")

    response = HttpResponse("\n".join(lines))
    response['Content-Disposition'] = 'attachment; filename="tags.csv"'
    return response


@require_GET
@login_required
def json_albums(request):
    albums = [{k: getattr(a, k) for k in Album.import_fields} for a in Album.objects.all()]
    for album in albums:
        album['date_acquired'] = datetime.strftime(album['date_acquired'], "%Y-%m-%d %H:%M:%S %Z")
    response = HttpResponse(json.dumps(albums, indent=4))
    response['Content-Disposition'] = 'attachment; filename="albums.json"'
    return response


@require_GET
@login_required
def json_artists(request):
    response = HttpResponse(json.dumps([a.to_json() for a in Artist.objects.all()], indent=4))
    response['Content-Disposition'] = 'attachment; filename="artists.json"'
    return response


@require_GET
@login_required
def json_colors(request):
    response = HttpResponse(json.dumps([c.to_json() for c in Color.objects.all()], indent=4))
    response['Content-Disposition'] = 'attachment; filename="colors.json"'
    return response


@require_GET
@login_required
def json_discs(request):
    response = HttpResponse(json.dumps([{
        "album_id": d.album.id,
        "name": d.name,
        "ordinal": d.ordinal,
    } for d in Disc.objects.all()], indent=4))
    response['Content-Disposition'] = 'attachment; filename="discs.json"'
    return response


@require_GET
@login_required
def json_songs(request):
    songs = [{k: getattr(a, k) for k in Song.import_fields} for a in Song.objects.all()]
    for song in songs:
        if song["artist"] is not None:
            song["artist"] = song["artist"].name
    response = HttpResponse(json.dumps(songs, indent=4))
    response['Content-Disposition'] = 'attachment; filename="songs.json"'
    return response


@require_GET
@login_required
def json_tags(request):
    response = HttpResponse(json.dumps([{
        "name": tag.name,
        "category": tag.category,
        "song_id": song.id,
    } for tag in Tag.objects.all() for song in tag.songs.all()], indent=4))
    response['Content-Disposition'] = 'attachment; filename="tags.json"'
    return response


@require_GET
@login_required
def json_tracks(request):
    response = HttpResponse(json.dumps([{
        "song_id": track.song.id,
        "album_id": track.album.id,
        "ordinal": track.ordinal,
        "disc_ordinal": track.disc,
    } for track in Track.objects.all()], indent=4))
    response['Content-Disposition'] = 'attachment; filename="tracks.json"'
    return response


def _playlist_response(request, songs, song_filters=None, album_filters=None, omni_filter=None):
    for song in songs:
        song.audit_export()

    playlist_name = request.GET.get("filename", "rhyme")
    config_name = request.GET.get("config")
    if config_name == "plex":
        count = create_plex_playlist(playlist_name, songs, song_filters, album_filters, omni_filter)
        return JsonResponse({
            "success": 1,
            "count": count,
            "name": playlist_name,
        })
    else:
        try:
            config = [c for c in settings.RHYME_EXPORT_CONFIGS if c["name"] == config_name][0]
        except IndexError:
            raise ExportConfigNotFoundException(f"Could not find {config_name}")
        filenames = [config["prefix"] + s.filename for s in songs]
        response = HttpResponse("\n".join(filenames))
        response['Content-Disposition'] = 'attachment; filename="{}.m3u"'.format(playlist_name)

    return response


@csrf_exempt
@require_POST
def plex_in(request, api_key):
    if api_key != settings.PLEX_API_KEY:
        return JsonResponse({"success": 0, "message": "Bad API key"})

    payload = json.loads(request.POST.get("payload"))
    event = payload.get("event")
    if event != "media.scrobble":
        return JsonResponse({"success": 0, "message": "Unsupported event"})

    plex_key = payload.get("Metadata", {}).get("key", None)
    if plex_key:
        song = Song.objects.filter(plex_key=plex_key).first()
        if song:
            song.play_count = song.play_count + 1
            song.last_play = datetime.now(timezone.utc)
            song.save()
            return JsonResponse({"success": 1, "message": "Updated {}".format(song)})

    return JsonResponse({"success": 0, "message": "Could not find song"})


def matrix(request):
    template = loader.get_template('rhyme/matrix.html')
    return HttpResponse(template.render({
        **_rhyme_context(),
        "title": "Matrix",
        "has_export": True,
    }, request))


def network(request):
    template = loader.get_template('rhyme/network.html')
    return HttpResponse(template.render({
        **_rhyme_context(),
        "title": "Network",
        "has_export": True,
        "categories": Tag.all_categories(),
        "strength": 50,
    }, request))


@require_GET
@login_required
def _stats(request, extra_context):
    template = loader.get_template('rhyme/stats.html')
    context = {
        **_rhyme_context(),
        **extra_context,
        "has_export": True,
    }
    return HttpResponse(template.render(context, request))


@require_GET
@login_required
def matrix_json(request):
    omni_filter = request.GET.get('omni_filter', '')
    album_filters = request.GET.get('album_filters')
    song_filters = request.GET.get('song_filters')

    attrs = ['rating', 'mood', 'energy']
    stats = Song.list(song_filters=song_filters,
                      album_filters=album_filters,
                      omni_filter=omni_filter).values(*attrs).annotate(count=Count('id')).order_by(*attrs)
    return JsonResponse({'stats': [s for s in stats]})


@require_GET
@login_required
def network_json(request):
    omni_filter = request.GET.get('omni_filter', '')
    album_filters = request.GET.get('album_filters')
    song_filters = request.GET.get('song_filters')

    song_ids = Song.list(song_filters=song_filters,
                         album_filters=album_filters,
                         omni_filter=omni_filter).values_list("id", flat=True)
    if len(song_ids) > Song.objects.count() / 2:
        include = None
        exclude = set(Song.objects.all().values_list("id", flat=True)).difference(song_ids)
    else:
        include = song_ids
        exclude = None

    def allow_song_id(song_id):
        return (include is not None and (song_id in include)) or (exclude is not None and (song_id not in exclude))

    strength = int(request.GET.get('strength', 50))
    category = request.GET.get('category')
    links = _network_tag_links(allow_song_id, strength, category)

    tag_ids = set([link["source"] for link in links] + [link["target"] for link in links])
    category_ids = {c: index for index, c in enumerate(Tag.all_categories())}
    nodes = {}
    for tag in Tag.objects.all():
        if tag.id not in tag_ids:
            continue
        for song in tag.songs.all():
            if allow_song_id(song.id):
                if tag.id not in nodes:
                    nodes[tag.id] = {
                        "id": tag.id,
                        "name": tag.name,
                        "count": 1,
                        "category": category_ids.get(tag.category, ""),
                    }
                else:
                    nodes[tag.id]["count"] += 1

    return JsonResponse({
        "nodes": [{
            "description": f"{node['name']}<br />{node['count']} {'song' if node['count'] == 1 else 'songs'}",
            **node,
        } for node in nodes.values()],
        "links": [{
            "description": f"""
                {nodes[link['source']]['name']} and {nodes[link['target']]['name']}
                <br />
                {link['value']} {'song' if link['value'] == 1 else 'songs'}
             """,
            **link,
        } for link in links],
    })


# TODO: add test
def _network_tag_links(allow_song_id, strength, category=None):
    if category:
        binds = [category, category]
        category_join = """
            inner join rhyme_tag tag1 on tag1.id = t1.tag_id and tag1.category = %s
            inner join rhyme_tag tag2 on tag2.id = t2.tag_id and tag2.category = %s
        """
    else:
        binds = []
        category_join = ""
    with connection.cursor() as cursor:
        cursor.execute("""
            select t1.song_id, t1.tag_id, t2.tag_id
            from rhyme_tag_songs t1
            inner join rhyme_tag_songs t2
            on t1.song_id = t2.song_id
            and t1.tag_id > t2.tag_id
            {category_join}
            group by t1.song_id, t1.tag_id, t2.tag_id
        """.format(category_join=category_join), binds)
        rows = cursor.fetchall()

    links = defaultdict(lambda: 0)
    for row in rows:
        song_id, first_tag, second_tag = row
        if allow_song_id(song_id):
            links[(first_tag, second_tag)] += 1

    return [{
        "source": key[0],
        "target": key[1],
        "value": value,
    } for key, value in links.items() if value >= strength]
