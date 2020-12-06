from datetime import datetime

from django.test import TestCase

from kilo.models import Day, Workout
from kilo.stats import best_erg, best_run, sum_erging, sum_running


class StatsTest(TestCase):
    date_format = "%Y-%m-%d"

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._create("2020-09-01", activity="erging", km=6, seconds=12 * 129)
        cls._create("2020-09-02", activity="erging", km=6, seconds=12 * 121.2)
        cls._create("2020-09-07", activity="erging", km=2, seconds=4 * 122)
        cls._create("2020-09-08", activity="erging", km=2, seconds=4 * 119)
        cls._create("2020-09-12", activity="erging", km=6, seconds=12 * 125)
        cls._create("2020-09-03", activity="running", mi=5, seconds=5 * 570)
        cls._create("2020-09-04", activity="running", mi=5, seconds=5 * 555)
        cls._create("2020-09-15", activity="running", mi=5, seconds=5 * 500)
        cls._create("2020-09-17", activity="running", mi=5, seconds=5 * 550)
        cls._create("2020-09-19", activity="running", mi=5, seconds=5 * 490)
        cls._create("2020-09-23", activity="running", mi=10, seconds=10 * 485)
        cls._create("2020-09-24", activity="running", mi=10, seconds=10 * 495)

    @classmethod
    def tearDownClass(cls):
        Day.objects.all().delete()
        Workout.objects.all().delete()
        super().tearDownClass()

    @classmethod
    def _create(cls, date, **workout_kwargs):
        day = Day(day=datetime.strptime(date, cls.date_format))
        day.save()
        Workout(day=day, **workout_kwargs).save()

    def _assertDate(self, obj, string):
        self.assertEqual(str(obj), string)

    def test_best_erg(self):
        days = Day.objects.all()
        self._assertDate(best_erg(days, 6).day.day, "2020-09-02")
        self._assertDate(best_erg(days, 2).day.day, "2020-09-08")

    def test_best_run(self):
        days = Day.objects.all()
        self._assertDate(best_run(days, upper_mi=7).day.day, "2020-09-19")
        self._assertDate(best_run(days, lower_mi=7).day.day, "2020-09-23")

    def test_sum_erging(self):
        self.assertEqual(sum_erging(Day.objects.all()), "22,000")

    def test_sum_running(self):
        self.assertEqual(sum_running(Day.objects.all()), "45")
