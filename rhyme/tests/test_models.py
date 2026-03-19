from datetime import datetime, timezone

from django.test import SimpleTestCase, TestCase

from rhyme.models import Album, Artist, Color, Playlist, PlaylistSong, Song, Tag, Track


class SongTest(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.artist = Artist.objects.create(name="Song Test Artist", genre="Rock")
        cls.album = Album.objects.create(name="Song Test Album")
        cls.song = Song.objects.create(name="Song Test Song", artist=cls.artist, rating=3, energy=4, mood=2)
        cls.track = Track.objects.create(song=cls.song, album=cls.album, ordinal=1)

    @classmethod
    def tearDownClass(cls):
        Artist.objects.all().delete()
        Album.objects.all().delete()
        Song.objects.all().delete()
        Track.objects.all().delete()

    def test_albums(self):
        albums = self.song.albums
        self.assertEqual(len(albums), 1)
        self.assertEqual(albums[0].id, self.album.id)

    def test_tags_no_category(self):
        tag1 = Tag.objects.create(name="st-tag1", category="colors")
        tag2 = Tag.objects.create(name="st-tag2", category="years")
        self.song.tag_set.add(tag1, tag2)
        tags = self.song.tags()
        self.assertIn("st-tag1", tags)
        self.assertIn("st-tag2", tags)

    def test_tags_with_category(self):
        tag1 = Tag.objects.create(name="st-red", category="colors")
        tag2 = Tag.objects.create(name="st-2020", category="years")
        self.song.tag_set.add(tag1, tag2)
        tags = self.song.tags(category="colors")
        self.assertEqual(tags, ["st-red"])

    def test_add_tag(self):
        result = self.song.add_tag("st-newtag")
        self.assertTrue(result)
        self.assertTrue(self.song.tag_set.filter(name="st-newtag").exists())
        # Duplicate returns False
        result = self.song.add_tag("st-newtag")
        self.assertFalse(result)

    def test_remove_tag(self):
        self.song.add_tag("st-removeme")
        result = self.song.remove_tag("st-removeme")
        self.assertTrue(result)
        self.assertFalse(self.song.tag_set.filter(name="st-removeme").exists())
        # Missing tag returns False
        result = self.song.remove_tag("st-removeme")
        self.assertFalse(result)

    def test_audit_export(self):
        self.song.refresh_from_db()
        initial_count = self.song.export_count
        self.song.audit_export()
        self.song.refresh_from_db()
        self.assertEqual(self.song.export_count, initial_count + 1)
        self.assertIsNotNone(self.song.exported_at)


class AlbumModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.artist1 = Artist.objects.create(name="Album Model Artist One", genre="Rock")
        cls.artist2 = Artist.objects.create(name="Album Model Artist Two", genre="Pop")

        # Album with one artist (for artist/completion/stats tests)
        cls.album_full = Album.objects.create(name="Full Album")
        cls.song_f1 = Song.objects.create(
            name="Full Song 1", artist=cls.artist1, rating=3, energy=4, mood=3)
        cls.song_f2 = Song.objects.create(
            name="Full Song 2", artist=cls.artist1, rating=4, energy=3, mood=4)
        Track.objects.create(song=cls.song_f1, album=cls.album_full, ordinal=1)
        Track.objects.create(song=cls.song_f2, album=cls.album_full, ordinal=2)

        # Album with partial ratings
        cls.album_partial = Album.objects.create(name="Partial Album")
        cls.song_p1 = Song.objects.create(
            name="Partial Song", artist=cls.artist1, rating=3, energy=4, mood=None)
        Track.objects.create(song=cls.song_p1, album=cls.album_partial, ordinal=1)

        # Album with no songs
        cls.album_empty = Album.objects.create(name="Empty Album")

        # Mix album with various artists
        cls.album_various = Album.objects.create(name="Various Artists Mix", is_mix=True)
        cls.song_v1 = Song.objects.create(
            name="Various Song 1", artist=cls.artist1, rating=5, energy=5, mood=5)
        cls.song_v2 = Song.objects.create(
            name="Various Song 2", artist=cls.artist2, rating=2, energy=2, mood=2)
        Track.objects.create(song=cls.song_v1, album=cls.album_various, ordinal=1)
        Track.objects.create(song=cls.song_v2, album=cls.album_various, ordinal=2)

        # Non-mix albums for alternate_sort tests
        cls.album_nonmix_a = Album.objects.create(name="Nonmix By Artist One", is_mix=False)
        cls.album_nonmix_b = Album.objects.create(name="Nonmix By Artist Two", is_mix=False)
        cls.song_na = Song.objects.create(
            name="Nonmix Song A", artist=cls.artist1, rating=3, energy=3, mood=3)
        cls.song_nb = Song.objects.create(
            name="Nonmix Song B", artist=cls.artist2, rating=3, energy=3, mood=3)
        Track.objects.create(song=cls.song_na, album=cls.album_nonmix_a, ordinal=1)
        Track.objects.create(song=cls.song_nb, album=cls.album_nonmix_b, ordinal=1)

        # Two mix albums for alternate_sort tests
        cls.album_mix_alpha = Album.objects.create(name="Alpha Mix", is_mix=True)
        cls.album_mix_beta = Album.objects.create(name="Beta Mix", is_mix=True)
        cls.song_ma = Song.objects.create(
            name="Mix Song Alpha", artist=cls.artist1, rating=3, energy=3, mood=3)
        cls.song_mb = Song.objects.create(
            name="Mix Song Beta", artist=cls.artist2, rating=3, energy=3, mood=3)
        Track.objects.create(song=cls.song_ma, album=cls.album_mix_alpha, ordinal=1)
        Track.objects.create(song=cls.song_mb, album=cls.album_mix_beta, ordinal=1)

    @classmethod
    def tearDownClass(cls):
        Artist.objects.all().delete()
        Album.objects.all().delete()
        Song.objects.all().delete()
        Track.objects.all().delete()
        Tag.objects.all().delete()

    def _fresh(self, album):
        """Return a fresh instance to avoid cached_property issues."""
        return Album.objects.get(id=album.id)

    def test_artist_single(self):
        self.assertEqual(self._fresh(self.album_full).artist, "Album Model Artist One")

    def test_artist_various(self):
        self.assertEqual(self._fresh(self.album_various).artist, "Various Artists")

    def test_completion_full(self):
        self.assertEqual(self._fresh(self.album_full).completion, 100)

    def test_completion_partial(self):
        # 1 song, 2 of 3 attributes set → 2/3 * 100
        expected = 2 * 100 / 3
        self.assertAlmostEqual(self._fresh(self.album_partial).completion, expected)

    def test_completion_empty(self):
        self.assertEqual(self._fresh(self.album_empty).completion, 0)

    def test_completion_text(self):
        self.assertEqual(self._fresh(self.album_full).completion_text, "")
        self.assertEqual(self._fresh(self.album_empty).completion_text, "")
        partial = self._fresh(self.album_partial)
        self.assertIn("%", partial.completion_text)
        self.assertIn("complete", partial.completion_text)

    def test_export_html_never(self):
        album = Album(name="Never Exported", export_count=0)
        self.assertEqual(album.export_html, "Never exported")

    def test_export_html_once(self):
        album = Album(name="Exported Once", export_count=1,
                      exported_at=datetime(2024, 1, 15, tzinfo=timezone.utc))
        self.assertIn("Exported once", album.export_html)

    def test_export_html_multiple(self):
        album = Album(name="Exported Many", export_count=3,
                      exported_at=datetime(2024, 1, 15, tzinfo=timezone.utc))
        self.assertIn("3 times", album.export_html)

    def test_alternate_sort_mix_vs_nonmix(self):
        sort_nonmix = Album.alternate_sort(self._fresh(self.album_full))
        sort_mix = Album.alternate_sort(self._fresh(self.album_various))
        self.assertLess(sort_nonmix, sort_mix)

    def test_alternate_sort_nonmix_by_artist(self):
        sort_a = Album.alternate_sort(self._fresh(self.album_nonmix_a))
        sort_b = Album.alternate_sort(self._fresh(self.album_nonmix_b))
        # artist1 name < artist2 name alphabetically
        self.assertLess(sort_a, sort_b)

    def test_alternate_sort_mix_by_name(self):
        sort_alpha = Album.alternate_sort(self._fresh(self.album_mix_alpha))
        sort_beta = Album.alternate_sort(self._fresh(self.album_mix_beta))
        # "alpha mix" < "beta mix"
        self.assertLess(sort_alpha, sort_beta)

    def test_stats(self):
        stats = self._fresh(self.album_full).stats()
        self.assertEqual(stats["rating"]["min"], 3)
        self.assertEqual(stats["rating"]["max"], 4)
        self.assertAlmostEqual(stats["rating"]["avg"], 3.5)
        self.assertEqual(stats["energy"]["min"], 3)
        self.assertEqual(stats["energy"]["max"], 4)
        self.assertEqual(stats["mood"]["min"], 3)
        self.assertEqual(stats["mood"]["max"], 4)

    def test_stats_nulls(self):
        stats = self._fresh(self.album_partial).stats()
        self.assertIsNone(stats["mood"]["min"])
        self.assertIsNone(stats["mood"]["avg"])
        self.assertIsNone(stats["mood"]["max"])
        self.assertEqual(stats["rating"]["min"], 3)

    def test_to_json_keys(self):
        result = self._fresh(self.album_full).to_json()
        expected_keys = {
            "acronym", "acronym_size", "artist", "cover_art_filename",
            "export_html", "color", "completion_text", "stats",
            "id", "name", "date_acquired", "export_count", "exported_at", "starred",
        }
        self.assertEqual(set(result.keys()), expected_keys)

    def test_tags(self):
        tag1 = Tag.objects.create(name="am-tag1")
        tag2 = Tag.objects.create(name="am-tag2")
        tag3 = Tag.objects.create(name="am-tag3")
        self.song_f1.tag_set.add(tag1, tag2)
        self.song_f2.tag_set.add(tag2, tag3)
        tags = self._fresh(self.album_full).tags()
        self.assertCountEqual(tags, ["am-tag1", "am-tag2", "am-tag3"])


class PlaylistTest(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.artist = Artist.objects.create(name="Playlist Test Artist", genre="Rock")
        cls.album = Album.objects.create(name="Playlist Test Album")
        cls.songs = []
        for i in range(5):
            song = Song.objects.create(
                name=f"Playlist Song {i}", artist=cls.artist, rating=i + 1)
            Track.objects.create(song=song, album=cls.album, ordinal=i + 1)
            cls.songs.append(song)

    @classmethod
    def tearDownClass(cls):
        Artist.objects.all().delete()
        Album.objects.all().delete()
        Song.objects.all().delete()
        Track.objects.all().delete()

    def test_all_filters_song_only(self):
        playlist = Playlist(song_filters="rating>=3")
        self.assertEqual(playlist.all_filters, "rating >= 3")

    def test_all_filters_combined(self):
        playlist = Playlist(song_filters="rating>=3", album_filters="is_mix=1", omni_filter="test")
        self.assertEqual(playlist.all_filters, "[test]; rating >= 3; is_mix = 1")

    def test_empty_playlist(self):
        playlist = Playlist.empty_playlist()
        # rating=10 matches nothing (max is 5)
        songs = list(playlist.natural_songs)
        self.assertEqual(len(songs), 0)

    def test_natural_songs(self):
        playlist = Playlist(song_filters="rating>=3")
        songs = list(playlist.natural_songs)
        # Songs with rating 3, 4, 5
        self.assertEqual(len(songs), 3)
        for song in songs:
            self.assertGreaterEqual(song.rating, 3)

    def test_songs_with_exclusion(self):
        playlist = Playlist.objects.create(name="pt-exclude-test", song_filters="rating>=3")
        # Exclude one of the matching songs
        excluded = self.songs[2]  # rating=3, matches filter
        PlaylistSong.objects.create(playlist=playlist, song=excluded, inclusion=False)
        song_ids = [s.id for s in playlist.songs]
        self.assertNotIn(excluded.id, song_ids)
        # Other matching songs still present
        self.assertIn(self.songs[3].id, song_ids)  # rating=4

    def test_songs_with_inclusion(self):
        playlist = Playlist.objects.create(name="pt-include-test", song_filters="rating>=4")
        # Include a song outside the filters
        added = self.songs[0]  # rating=1, doesn't match rating>=4
        PlaylistSong.objects.create(playlist=playlist, song=added, inclusion=True)
        song_ids = [s.id for s in playlist.songs]
        self.assertIn(added.id, song_ids)
        # Songs matching filter are still present
        self.assertIn(self.songs[3].id, song_ids)  # rating=4


class ArtistTest(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.artist1 = Artist.objects.create(name="Genre Test Artist 1", genre="Rock")
        cls.artist2 = Artist.objects.create(name="Genre Test Artist 2", genre="Pop")
        cls.artist3 = Artist.objects.create(name="Genre Test Artist 3", genre="Rock")
        cls.artist4 = Artist.objects.create(name="Genre Test Artist 4", genre="")

    @classmethod
    def tearDownClass(cls):
        Artist.objects.all().delete()

    def test_all_genres(self):
        genres = Artist.all_genres()
        self.assertEqual(genres, ["Pop", "Rock"])


class TagTest(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tag1 = Tag.objects.create(name="tt-red", category="colors")
        cls.tag2 = Tag.objects.create(name="tt-blue", category="colors")
        cls.tag3 = Tag.objects.create(name="tt-2020", category="years")
        cls.tag4 = Tag.objects.create(name="tt-uncategorized")

    @classmethod
    def tearDownClass(cls):
        Tag.objects.all().delete()

    def test_all_categories(self):
        categories = Tag.all_categories()
        self.assertIn("colors", categories)
        self.assertIn("years", categories)
        self.assertEqual(categories, sorted(categories))
        self.assertNotIn(None, categories)


class ColorTest(SimpleTestCase):
    def test_to_json(self):
        color = Color(name="red", hex_code="ff0000", white_text=True)
        result = color.to_json()
        self.assertEqual(result["name"], "red")
        self.assertEqual(result["hex_code"], "ff0000")
        self.assertEqual(result["white_text"], True)
