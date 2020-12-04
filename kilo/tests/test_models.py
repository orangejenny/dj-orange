from datetime import datetime, timedelta

from django.test import SimpleTestCase, TestCase

from kilo.models import Day, Workout

class SimpleWorkoutTest(SimpleTestCase):
    def test_summary(self):
        self.assertEqual(Workout(
            activity="erging",
            km=6,
            seconds=24 * 60 + 47.9,
        ).summary, "6 km in 24:47.9 (2:04.0)")
        self.assertEqual(Workout(
            activity="running",
            mi=4,
            seconds=35 * 60 + 31,
        ).summary, "4 mi in 35:31 (8:53)")
        self.assertEqual(Workout(
            activity="stairs",
        ).summary, "")
        self.assertEqual(Workout(
            activity="erging",
            m=500,
            sets=4,
        ).summary, "4 x 500 m")
        self.assertEqual(Workout(
            activity="deadlifts",
            sets=5,
            reps=1,
            weight=185,
        ).summary, "5 x 1 @ 185lb")

    def test_time(self):
        self.assertIsNone(Workout().time)
        self.assertEqual(Workout(seconds=2).time, "0:02")
        self.assertEqual(Workout(seconds=3.1).time, "0:03.1")
        self.assertEqual(Workout(seconds=45).time, "0:45")
        self.assertEqual(Workout(seconds=492).time, "8:12")
        self.assertEqual(Workout(seconds=1024).time, "17:04")
        self.assertEqual(Workout(seconds=5111).time, "1:25:11")

    def test_distance(self):
        with self.assertRaises(ValueError):
            Workout(m=500, km=0.5)

        self.assertIsNone(Workout().mi)
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
        self.assertIsNone(Workout().pace)
        self.assertIsNone(Workout(km=5).pace)
        self.assertIsNone(Workout(seconds=50).pace)
        self.assertEqual(Workout(km=2, seconds=476.8).pace, "1:59.2")
        self.assertEqual(Workout(mi=5, seconds=2447).pace, "8:09")
        self.assertEqual(Workout(m=500, seconds=111).pace, "1:51")


class WorkoutTest(TestCase):
    today = datetime.now().date()

    def tearDown(self):
        Day.objects.all().delete()
        Workout.objects.all().delete()

    def test_stats(self):
        day1 = Day(day=self.today)
        day1.save()
        stairs = Workout(activity="stairs", day=day1)
        self.assertIsNone(stairs.primary_stat())
        self.assertEqual(stairs.secondary_stat(), day1.day)

        day2 = Day(day=self.today - timedelta(days=1))
        day2.save()
        erg = Workout(
            activity="erging",
            km=6,
            seconds=24 * 60 + 37.2,
            day=day2,
        )
        self.assertEqual(erg.primary_stat(), "2:03.1")
        self.assertEqual(erg.secondary_stat(), day2.day)

        day3 = Day(day=self.today - timedelta(days=2))
        day3.save()
        run = Workout(
            activity="running",
            mi=5,
            seconds=5 * 491,
            day=day3,
        )
        self.assertEqual(run.primary_stat(), "5 mi at 8:11")
        self.assertEqual(run.secondary_stat(), day3.day)
