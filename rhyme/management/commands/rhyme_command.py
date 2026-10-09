from django.core.management.base import BaseCommand

from rhyme.models import Playlist, PlaylistSong, Song
from rhyme.plex import create_plex_playlist

class Command(BaseCommand):
    def handle(self, *args, **options):
        raise Exception("Subclasses should override this method")

    def get_song(self):
        seed = None
        while seed is None:
            name = input("Song name? ")
            songs = Song.objects.filter(name__icontains=name)
            if songs.count() > 7:
                artist = input("Artist? ")
                songs = songs.filter(artist__name__icontains=artist)
            if songs.count() == 1:
                seed = songs.first()
            elif songs.count() > 1:
                self.print_numbered_list(songs)
                ordinal = input("Which song? ")
                try:
                    seed = songs[int(ordinal) - 1]
                except (ValueError, IndexError):
                    pass
        return seed

    def get_playlist(self):
        playlists = Playlist.objects.all().order_by("name")
        key = None
        while key is None:
            self.print_numbered_list(playlists)
            key = input("Playlist? ")
            try:
                key = int(key) - 1
            except (IndexError, ValueError):
                key = None
        return playlists[key]

    def export_playlist(self, song_ids, display=True):
        if display:
            for song_id in song_ids:
                print(Song.objects.get(id=song_id))

        command = input("\nExport to (r)hyme, (p)lex? ").lower()
        if command == "r":
            playlist = Playlist.empty_playlist()
            playlist.name = input("Name? ")
            playlist.save()
            for song_id in song_ids:
                PlaylistSong(playlist_id=playlist.id, song_id=song_id, inclusion=True).save()
        elif command == "p":
            playlist_name = input("Name? ")
            create_plex_playlist(playlist_name, Song.objects.filter(id__in=song_ids))

    def print_numbered_list(self, things):
        for index, thing in enumerate(things):
            print(f"{index + 1}) {thing}")
