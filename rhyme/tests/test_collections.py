from django.test import SimpleTestCase

from rhyme.models import Album

class AlbumTest(SimpleTestCase):
    def test_acronym(self):
        album = Album(id=1, name="Liars")
        self.assertEqual(album.acronym, "L")
        self.assertEqual(album.acronym_size, "solo")

        album = Album(id=1, name="A Question of Time")
        self.assertEqual(album.acronym, "AQoT")
        self.assertEqual(album.acronym_size, "medium")

        album = Album(id=1, name="Mellon Collie and the Infinite Sadness: Twilight to Starlight")
        self.assertEqual(album.acronym, "MCatISTtS")
        self.assertEqual(album.acronym_size, "xsmall")

    # TODO: tests for other Album calculations
