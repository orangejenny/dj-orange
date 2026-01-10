import re

from plexapi.exceptions import NotFound
from plexapi.myplex import MyPlexAccount
from plexapi.playlist import Playlist as PlexPlaylist
from rhyme.models import Playlist

from django.conf import settings

from Levenshtein import distance

def plex_server():
    account = MyPlexAccount(settings.PLEX_USERNAME, settings.PLEX_PASSWORD)
    return account.resource(settings.PLEX_SERVER).connect()

def plex_library(server=None):
    server = server or plex_server()
    return server.library.section('Music')

# Songs in rhyme but missing from plex
def missing_songs(**kwargs):
    from rhyme.models import Song
    return list(Song.objects.filter(plex_key__isnull=True, **kwargs))

# Returns list of (song_count, artist_name) tuples
def missing_songs_by_count(**kwargs):
    from collections import defaultdict
    counts = defaultdict(list)
    for song in missing_songs(**kwargs):
        counts[song.artist.name].append(song)
    return sorted([(len(songs), artist) for artist, songs in counts.items()])

def missing_songs_by_album(name):
   from rhyme.models import Album
   return [t.song for t in Album.objects.filter(name__icontains=name).first().tracks if not t.song.plex_key]

# Update plex key and guid for a set of songs missing it
# Use plex_key to search by that album/artist instead of the rhyme song's artist
def add_plex_ids(library, songs):
    updated = 0
    songs = list(songs)
    for song in songs:
        try:
            result = library.get(song.artist.name).get(song.name)
            song.plex_guid = result.guid
            song.plex_key = result.key
            song.save()
            updated += 1
        except Exception as e:
            print("Could not find {} - {}: {}".format(song.artist.name, song.name, str(e)))
    print("Updated {} of {} songs".format(updated, len(songs)))

def plex_options(library, song, plex_key=None):
    ancestor = library.fetchItem(plex_key) if plex_key else library.get(song.artist.name)
    needle = song.name
    options = [t for t in ancestor.tracks() if needle in t.title]
    if not len(options):
        needle = song.name.lower()
        options = [t for t in ancestor.tracks() if needle in t.title.lower()]
        if not len(options):
            needle = re.sub("[^a-z]+", "", needle)
            options = [t for t in ancestor.tracks() if needle in re.sub("[^a-z]+", "", t.title)]
    options = sorted(options, key=lambda option: distance(song.name, option))
    options = options[:5]
    return options

# Add the given plex key (add associated guid) to the given artist's song,
# which should be the only missing song by that artist
def fix_single(library, artist, plex_key_id):
    save_match(library, missing_songs(artist__name=artist)[0], "/library/metadata/" + plex_key_id)

# Add the given plex key (add associated guid) to the given song
def save_match(library, rhyme, plex_key):
    plex = library.fetchItem(plex_key)
    rhyme.plex_guid = plex.guid
    rhyme.plex_key = plex.key
    rhyme.save()

# Get plex tracks for given artist and song title substring
def get_tracks(library, artist, song_name_query):
   return [t for t in library.get(artist).tracks() if song_name_query in t]

# Get rhyme songs for given artist and song title substring
def get_songs(artist, song_name_query):
    return Song.objects.filter(artist__name=artist, name__icontains=song_name_query)

# Create playlist on Plex server. Slow.
def create_plex_playlist(name, songs, song_filters=None, album_filters=None, omni_filter=None):
    server = plex_server()
    library = plex_library(server)
    items = []
    for song in songs:
        if song.plex_key:
            try:
                items.append(library.fetchItem(song.plex_key))
            except NotFound:
                pass
    plex_playlist = PlexPlaylist.create(server, name, items=items, section='Music')
    if song_filters or album_filters or omni_filter:
        playlist = Playlist(
            name=name,
            plex_guid=plex_playlist.guid,
            plex_key=plex_playlist.key,
            plex_count=len(items),
            song_filters=song_filters,
            album_filters=album_filters,
            omni_filter=omni_filter,
        )
        playlist.save()

    return len(items)
