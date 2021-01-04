from django.core.exceptions import ValidationError
from django.test import TestCase

from rhyme.models import Album, Artist, Playlist, Song, Track


class FilterTest(TestCase):
    @classmethod
    def setUpClass(cls):
        # 3 artists
        artists = [
            Artist(name="Artist1", genre="Industrial"),
            Artist(name="Artist2", genre="Pop"),
            Artist(name="Artist3", genre="Dance"),
        ]

        # 3 albums
        albums = [
            Album(name="Bad Album by Artist1", is_mix=False),
            Album(name="Mix by Artist1 and Artist2", is_mix=True),
            Album(name="Good Album by Artist3", is_mix=False),
        ]

        for obj in artists + albums:
            obj.save()

        # 125 songs
        for rating in range(1, 6):
            for energy in range(1, 6):
                for mood in range(1, 6):
                    if rating in (1, 2):
                        album = albums[0]
                        artist = artists[0]
                    elif rating == 3:
                        album = albums[1]
                        artist = artists[0] if energy % 2 == 0 else artists[1]
                    else:
                        album = albums[2]
                        artist = artists[2]
                    song = Song(artist=artist, name=f"Song {'*' * rating} {'!' * energy} {'#' * mood}",
                                rating=rating, energy=energy, mood=mood,
                                starred=rating > 3 and energy > 4,
                                time=30 * rating + 20 * energy + 10 * mood,
                                year=1990 + rating + energy + mood)
                    song.save()
                    Track(song=song, album=album, ordinal=len(album.tracks) + 1).save()

    @classmethod
    def tearDownClass(cls):
        Artist.objects.all().delete()
        Album.objects.all().delete()
        Song.objects.all().delete()
        Track.objects.all().delete()


class SongFilterTest(FilterTest):
    def test_starred(self):
        starred_names = {
            "Song ***** !!!!! #####",
            "Song ***** !!!!! ####",
            "Song ***** !!!!! ###",
            "Song ***** !!!!! ##",
            "Song ***** !!!!! #",
            "Song **** !!!!! #####",
            "Song **** !!!!! ####",
            "Song **** !!!!! ###",
            "Song **** !!!!! ##",
            "Song **** !!!!! #",
        }

        names = [s.name for s in Song.list(song_filters="starred=1")]
        self.assertEqual(len(names), 10)
        self.assertEqual(starred_names, set(names))

        names = [s.name for s in Song.list(song_filters="starred=0")]
        self.assertEqual(len(names), 115)
        self.assertEqual(set(names) & starred_names, set())

        with self.assertRaises(ValidationError):
            Song.list(song_filters="starred=2")

    def test_artist(self):
        artist_names = [s.artist.name for s in Song.list(song_filters="artist=Artist3")]
        self.assertEqual(len(artist_names), 50)
        self.assertEqual(set(artist_names), {"Artist3"})
        songs = Song.list(song_filters="artist=Artist4")
        self.assertEqual(len(songs), 0)

        songs = Song.list(song_filters="artist*=Artist1&&artist*=Artist2")
        self.assertEqual(len(songs), 0)

    def test_genre(self):
        genres = [s.artist.genre for s in Song.list(song_filters="genre=Industrial")]
        self.assertEqual(len(genres), 60)
        self.assertEqual(set(genres), {"Industrial"})

    def test_name(self):
        names = [s.name for s in Song.list(song_filters="name=Song **** !!!!! ###")]
        self.assertEqual(len(names), 1)
        self.assertEqual(names[0], "Song **** !!!!! ###")
        names = [s.name for s in Song.list(song_filters="name*=Song **** !!!!! ###")]
        self.assertEqual(len(names), 3)
        self.assertEqual({
            "Song **** !!!!! ###",
            "Song **** !!!!! ####",
            "Song **** !!!!! #####",
        }, set(names))

    def test_length(self):
        times = [s.time for s in Song.list(song_filters="time>=200")]
        self.assertEqual(len(times), 50)
        self.assertEqual(min(times), 200)
        self.assertEqual(max(times), 300)

        times = [s.time for s in Song.list(song_filters="time<=100")]
        self.assertEqual(len(times), 11)
        self.assertEqual(min(times), 60)
        self.assertEqual(max(times), 100)

    def test_year(self):
        years = [s.year for s in Song.list(song_filters="time>=200")]
        self.assertEqual(len(years), 50)
        self.assertEqual(min(years), 1998)
        self.assertEqual(max(years), 2005)

    def test_ratings(self):
        self.assertEqual(len(Song.list(song_filters="energy=5")), 25)
        self.assertEqual(len(Song.list(song_filters="energy=5&&mood=3")), 5)
        self.assertEqual(len(Song.list(song_filters="rating>=4||mood<=2")), 80)

    def test_album_name(self):
        songs = Song.list(album_filters="name*=Mix")
        self.assertEqual(len(songs), 25)
        album_song_ids = {t.song.id for t in Album.objects.get(name__contains="Mix").tracks}
        self.assertEqual(album_song_ids, {s.id for s in songs})

    def test_album_is_mix(self):
        songs = Song.list(album_filters="is_mix=1")
        self.assertEqual(len(songs), 25)
        album_song_ids = {t.song.id for t in Album.objects.get(name__contains="Mix").tracks}
        self.assertEqual(album_song_ids, {s.id for s in songs})

    def test_playlist(self):
        playlist = Playlist(name='123', song_filters="energy=5")
        playlist.save()
        self.assertEqual(
            {s.id for s in Song.list(song_filters="playlist*=123")},
            {s.id for s in Song.list(song_filters="energy=5")}
        )
        playlist.delete()

    def test_omni_filter(self):
        names = [s.name for s in Song.list(omni_filter="Song **** !!!!! ###")]
        self.assertEqual(len(names), 6)
        self.assertEqual(set(names), {
            "Song **** !!!!! ###",
            "Song **** !!!!! ####",
            "Song **** !!!!! #####",
            "Song ***** !!!!! ###",
            "Song ***** !!!!! ####",
            "Song ***** !!!!! #####",
        })

    def test_all_filter_types(self):
        songs = Song.list(song_filters="mood=4", album_filters="is_mix=1", omni_filter="!!!!!")
        self.assertEqual(len(songs), 1)
        self.assertEqual(songs[0].name, "Song *** !!!!! ####")


class AlbumFilterTest(FilterTest):
    def test_name(self):
        albums = Album.list(album_filters="name*=Mix")
        self.assertEqual(len(albums), 1)
        self.assertEqual(albums[0].name, "Mix by Artist1 and Artist2")

    def test_rating(self):
        albums = Album.list(song_filters="rating=5")
        self.assertEqual(len(albums), 1)
        self.assertEqual(albums[0].name, "Good Album by Artist3")
