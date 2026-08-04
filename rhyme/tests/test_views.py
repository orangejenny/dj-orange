import json

from django.contrib.auth.models import User
from django.test import TestCase, override_settings

from rhyme.exceptions import ExportConfigNotFoundException
from rhyme.models import Album, Artist, Playlist, PlaylistSong, Song, Tag, Track


class RhymeViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.create_user(username="rhyme-testuser", password="testpass")
        cls.artist = Artist.objects.create(name="View Test Artist", genre="Rock")
        cls.album = Album.objects.create(name="View Test Album")
        cls.song1 = Song.objects.create(
            name="View Song 1", artist=cls.artist, rating=3, energy=4, mood=3,
            filename="view_artist/song1.mp3")
        cls.song2 = Song.objects.create(
            name="View Song 2", artist=cls.artist, rating=4, energy=3, mood=4,
            filename="view_artist/song2.mp3")
        cls.track1 = Track.objects.create(song=cls.song1, album=cls.album, ordinal=1)
        cls.track2 = Track.objects.create(song=cls.song2, album=cls.album, ordinal=2)

    @classmethod
    def tearDownClass(cls):
        Track.objects.all().delete()
        Song.objects.all().delete()
        Album.objects.all().delete()
        Artist.objects.all().delete()
        User.objects.all().delete()
        Tag.objects.all().delete()
        Playlist.objects.all().delete()

    def setUp(self):
        self.client.force_login(self.user)


class SongListTest(RhymeViewTest):
    def test_basic(self):
        response = self.client.get("/rhyme/songs/list/", {"page": 1})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("items", data)
        self.assertIn("count", data)
        self.assertIn("more", data)

    def test_pagination(self):
        response = self.client.get("/rhyme/songs/list/", {"page": 1, "songs_per_page": 1})
        data = response.json()
        self.assertTrue(data["more"])
        self.assertEqual(len(data["items"]), 1)

    def test_song_filter(self):
        response = self.client.get("/rhyme/songs/list/", {"page": 1, "song_filters": "rating>=4"})
        data = response.json()
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["items"][0]["name"], "View Song 2")

    def test_album_id(self):
        response = self.client.get("/rhyme/songs/list/", {"album_id": self.album.id})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("disc_names", data)
        self.assertEqual(data["count"], 2)


class SongUpdateTest(RhymeViewTest):
    def test_update_rating(self):
        response = self.client.post("/rhyme/songs/update/", {
            "id": self.song1.id,
            "field": "rating",
            "value": "5",
        })
        self.assertEqual(response.json()["success"], 1)
        self.song1.refresh_from_db()
        self.assertEqual(self.song1.rating, 5)

    def test_update_tags(self):
        response = self.client.post("/rhyme/songs/update/", {
            "id": self.song1.id,
            "field": "tags",
            "value": "rock pop",
        })
        self.assertEqual(response.json()["success"], 1)
        tag_names = set(self.song1.tag_set.values_list("name", flat=True))
        self.assertEqual(tag_names, {"rock", "pop"})

    def test_update_tags_normalizes_whitespace(self):
        response = self.client.post("/rhyme/songs/update/", {
            "id": self.song1.id,
            "field": "tags",
            "value": " rock  pop ",
        })
        self.assertEqual(response.json()["success"], 1)
        tag_names = set(self.song1.tag_set.values_list("name", flat=True))
        self.assertEqual(tag_names, {"rock", "pop"})

    def test_update_starred_with_playlist(self):
        playlist = Playlist.objects.create(name="sv-star-playlist")
        response = self.client.post("/rhyme/songs/update/", {
            "id": self.song1.id,
            "field": "starred",
            "value": "True",
            "playlist_name": "sv-star-playlist",
        })
        self.assertEqual(response.json()["success"], 1)
        self.assertTrue(PlaylistSong.objects.filter(playlist=playlist, song=self.song1).exists())

    def test_update_starred_toggle(self):
        playlist = Playlist.objects.create(name="sv-toggle-playlist")
        # First call: creates PlaylistSong
        self.client.post("/rhyme/songs/update/", {
            "id": self.song1.id,
            "field": "starred",
            "value": "True",
            "playlist_name": "sv-toggle-playlist",
        })
        self.assertTrue(PlaylistSong.objects.filter(playlist=playlist, song=self.song1).exists())
        # Second call: removes it
        self.client.post("/rhyme/songs/update/", {
            "id": self.song1.id,
            "field": "starred",
            "value": "True",
            "playlist_name": "sv-toggle-playlist",
        })
        self.assertFalse(PlaylistSong.objects.filter(playlist=playlist, song=self.song1).exists())


class AlbumListTest(RhymeViewTest):
    def test_basic(self):
        response = self.client.get("/rhyme/albums/list/", {"page": 1})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("items", data)
        self.assertIn("count", data)
        self.assertIn("more", data)

    def test_filter(self):
        response = self.client.get("/rhyme/albums/list/", {
            "page": 1,
            "album_filters": "name=View Test Album",
        })
        data = response.json()
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["items"][0]["name"], "View Test Album")


class ChoicesTest(RhymeViewTest):
    def test_artist_choices(self):
        response = self.client.get("/rhyme/artists/choices/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        names = [item["text"] for item in data["items"]]
        self.assertIn("View Test Artist", names)
        self.assertEqual(sorted(names), names)

    def test_artist_choices_search(self):
        response = self.client.get("/rhyme/artists/choices/", {"term": "View Test"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data["items"]), 1)
        self.assertEqual(data["items"][0]["text"], "View Test Artist")

    def test_tag_choices(self):
        Tag.objects.create(name="choices-test-tag")
        response = self.client.get("/rhyme/tags/choices/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        names = [item["text"] for item in data["items"]]
        self.assertIn("choices-test-tag", names)

    def test_playlist_choices(self):
        Playlist.objects.create(name="choices-test-playlist")
        response = self.client.get("/rhyme/playlist/choices/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        names = [item["text"] for item in data["items"]]
        self.assertIn("choices-test-playlist", names)


class MatrixJsonTest(RhymeViewTest):
    def test_basic(self):
        response = self.client.get("/rhyme/stats/matrix/json/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("stats", data)
        self.assertIsInstance(data["stats"], list)
        if data["stats"]:
            stat = data["stats"][0]
            for key in ["rating", "mood", "energy", "count"]:
                self.assertIn(key, stat)


class NetworkJsonTest(RhymeViewTest):
    def test_basic(self):
        response = self.client.get("/rhyme/stats/network/json/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("nodes", data)
        self.assertIn("links", data)
        self.assertIsInstance(data["nodes"], list)
        self.assertIsInstance(data["links"], list)

    def test_category_filter(self):
        response = self.client.get("/rhyme/stats/network/json/", {"category": "colors"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("nodes", data)
        self.assertIn("links", data)


_EXPORT_CONFIGS = [{"name": "local", "prefix": "/music/"}]


class SongExportTest(RhymeViewTest):
    @override_settings(RHYME_EXPORT_CONFIGS=_EXPORT_CONFIGS)
    def test_export_m3u(self):
        response = self.client.get("/rhyme/songs/export/", {"config": "local"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("attachment", response["Content-Disposition"])
        content = response.content.decode()
        self.assertIn("/music/", content)

    def test_export_rhyme(self):
        response = self.client.get("/rhyme/songs/export/", {
            "config": "rhyme",
            "filename": "sv-testplaylist",
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["success"], 1)
        self.assertTrue(Playlist.objects.filter(name="sv-testplaylist").exists())

    @override_settings(RHYME_EXPORT_CONFIGS=_EXPORT_CONFIGS)
    def test_export_unknown_config(self):
        with self.assertRaises(ExportConfigNotFoundException):
            self.client.get("/rhyme/songs/export/", {"config": "unknown-config"})
