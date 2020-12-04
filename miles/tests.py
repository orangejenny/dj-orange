from django.test import SimpleTestCase

from miles.models import Workout

class WorkoutTest(SimpleTestCase):
    def test_time(self):
        self.assertEqual(Workout().time, None)
        self.assertEqual(Workout(seconds=2).time, "0:02")
        self.assertEqual(Workout(seconds=3.1).time, "0:03.1")
        self.assertEqual(Workout(seconds=45).time, "0:45")
        self.assertEqual(Workout(seconds=492).time, "8:12")
        self.assertEqual(Workout(seconds=1024).time, "17:04")
        self.assertEqual(Workout(seconds=5111).time, "1:25:11")

    def test_distance(self):
        with self.assertRaises(ValueError):
            Workout(m=500, km=0.5)

        self.assertEqual(Workout().mi, None)
        self.assertEqual(Workout(mi=5).mi, 5)
        self.assertEqual(Workout(mi=5).km, 8)
        self.assertEqual(Workout(mi=5).m, 8045)
        self.assertEqual(Workout(km=2).mi, 1.25)
        self.assertEqual(Workout(km=2).km, 2)
        self.assertEqual(Workout(km=2).m, 2000)
        self.assertEqual(Workout(m=500).mi, 0.31)
        self.assertEqual(Workout(m=500).km, 0.5)
        self.assertEqual(Workout(m=500).m, 500)

    def test_pace(self):
        self.assertEqual(Workout().pace, None)
        self.assertEqual(Workout(km=5).pace, None)
        self.assertEqual(Workout(seconds=50).pace, None)
        self.assertEqual(Workout(km=2, seconds=476.8).pace, "1:59.2")
        self.assertEqual(Workout(mi=5, seconds=2447).pace, "8:09")
        self.assertEqual(Workout(m=500, seconds=111).pace, "1:51")
