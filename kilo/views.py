import json

from collections import defaultdict, Counter
from datetime import datetime, timedelta

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET

from kilo.models import Day, Workout
from kilo.stats import best_erg, best_run, sum_erging, sum_running


@login_required
def base(request):
    if request.method == "POST":
        post_data = json.loads(request.body.decode("utf-8"))['day']

        date = f"{post_data.get('year')}-{post_data.get('month')}-{post_data.get('dayOfMonth')}"
        try:
            datetime(
                int(post_data.get('year')),
                int(post_data.get('month')),
                int(post_data.get('dayOfMonth')),
            )
        except ValueError as e:
            return JsonResponse({
                "error": f"Received invalid date {date}: " + str(e),
            })
        day = Day.objects.filter(day=date).first()
        if day:
            if day.id != int(post_data.get('id') or 0):
                return JsonResponse({
                    "error": f"Attempting to duplicate {day.day}",
                })
        else:
            day = Day()
        day.day = date
        day.notes = post_data.get('notes')
        day.save()

        for workout in day.workout_set.all():
            if workout.id not in [int(w.get('id')) for w in post_data.get("workouts", []) if w.get('id')]:
                workout.delete()

        for workout_data in post_data.get("workouts", []):
            try:
                workout = Workout.objects.get(id=workout_data.get('id'))
            except Workout.DoesNotExist:
                workout = Workout(day=day)
            for attr in ['activity', 'seconds', 'distance', 'distance_unit', 'sets', 'reps', 'weight']:
                setattr(workout, attr, workout_data.get(attr))
            if not workout.distance:
                workout.distance_unit = None
            if workout.activity:
                workout.save()

        return JsonResponse({
            "success": 1,
            "day": day.to_json(),
        })

    return HttpResponse(render(request, "kilo/base.html"))


@require_GET
@login_required
def recent(request):
    today = datetime.now().date()
    days = []

    for delta in range(0, 15):
        day_index = today - timedelta(days=delta + 1)
        try:
            day = Day.objects.get(day=day_index)
        except Day.DoesNotExist as e:
            day = Day(day=day_index)
        days.append(day)

    return _days(days)


@require_GET
@login_required
def history(request):
    days = Day.get_recent_days(90)
    return _days(days)


def _days(days):
    activity_counter = Counter(Workout.objects.all().values_list("activity", flat=True))
    common_activities = [a[0] for a in activity_counter.most_common(3)]
    other_activities = sorted([a for a in activity_counter.keys() if a not in common_activities])

    return JsonResponse({
        "all_activities": common_activities + other_activities,
        "all_distance_units": [u[0] for u in Workout.DISTANCE_UNITS],
        "recent_days": [_format_day(d) for d in days],
        "stats": _get_stats(),
        "frequency_graph_data": _get_frequency_graph_data(),
        "pace_graph_data": _get_pace_graph_data(),
    })


def _format_day(day):
    return {
        "id": day.id,
        "day": day.day,
        "notes": day.notes,
        "workouts": [w.to_json() for w in day.workout_set.all()] if day.id else [],
    }


def _get_stats():
    last_year_days = Day.get_recent_days(365)
    last_month_days = Day.get_recent_days(30)

    erging_stats = []
    erging_stats.append({
        "name": "Past Month",
        "primary": sum_erging(last_month_days),
        "secondary": "total m erged"}
    )
    workout = best_erg(last_month_days, km=2)
    if workout:
        erging_stats.append({
            "name": "Past Month's Best 2k",
            "primary": workout.primary_stat(),
            "secondary": workout.secondary_stat(),
        })
    workout = best_erg(last_month_days, km=6)
    if workout:
        erging_stats.append({
            "name": "Past Month's Best 6k",
            "primary": workout.primary_stat(),
            "secondary": workout.secondary_stat(),
        })
    workout = best_erg(last_year_days, km=2)
    if workout:
        erging_stats.append({
            "name": "Past Year's Best 2k",
            "primary": workout.primary_stat(),
            "secondary": workout.secondary_stat(),
        })
    workout = best_erg(last_year_days, km=6)
    if workout:
        erging_stats.append({
            "name": "Past Year's Best 6k",
            "primary": workout.primary_stat(),
            "secondary": workout.secondary_stat(),
        })

    running_stats = []
    running_stats.append({
        "name": "Past Month",
        "primary": sum_running(last_month_days),
        "secondary": "total miles run",
    })
    boundary = 7
    workout = best_run(last_month_days, upper_mi=boundary)
    if workout:
        running_stats.append({
            "name": "Past Month's Best Short Run",
            "primary": workout.primary_stat(),
            "secondary": workout.secondary_stat(),
        })
    workout = best_run(last_month_days, lower_mi=boundary)
    if workout:
        running_stats.append({
            "name": "Past Month's Best Long Run",
            "primary": workout.primary_stat(),
            "secondary": workout.secondary_stat(),
        })
    workout = best_run(last_year_days, upper_mi=boundary)
    if workout:
        running_stats.append({
            "name": "Past Year's Best Short Run",
            "primary": workout.primary_stat(),
            "secondary": workout.secondary_stat(),
        })
    workout = best_run(last_year_days, lower_mi=boundary)
    if workout:
        running_stats.append({
            "name": "Past Year's Best Long Run",
            "primary": workout.primary_stat(),
            "secondary": workout.secondary_stat(),
        })

    return [{
        "title": "Erging",
        "stats": erging_stats,
    }, {
        "title": "Running",
        "stats": running_stats,
    }]


def _get_frequency_graph_data():
    days = Day.get_recent_days(180)

    data = {}
    data["x"] = "day"
    all_activities = {w.activity for d in days for w in d.workout_set.all()}
    day_series = []
    series = defaultdict(list)
    index = days.last().day
    while index <= datetime.now().date():
        day_series.append(index.strftime("%Y-%m-%d"))
        next_index = index + timedelta(days=7)
        activity_counts = defaultdict(lambda: 0)
        for day in days.filter(day__gte=index, day__lt=next_index):
            activity_counts[day.primary_activity()] += 1
        for activity in all_activities:
            series[activity].append(activity_counts[activity] or 0)
        index = next_index
    data["columns"] = [["day"] + day_series] + [
        [activity] + counts
        for activity, counts in series.items()
    ]
    data["types"] = {activity: "area-spline" for activity in all_activities}
    data["groups"] = [list(all_activities)]

    return data


def _get_pace_graph_data():
    days = Day.get_recent_days(90)

    def interval_filter(wset, activity, distance_test):
        if any([w.activity != activity for w in wset.all()]):
            return False
        return all([distance_test(w.km) for w in wset.all()])

    def single_workout_filter(wset, activity, distance_test):
        if wset.count() != 1:
            return False
        if wset.first().activity != activity:
            return False
        return distance_test(wset.first().km)

    series_map = {
        "500m": lambda wset: interval_filter(wset, "erging", lambda km: km == 0.5),
        "1000m": lambda wset: interval_filter(wset, "erging", lambda km: km == 1),
        "2k": lambda wset: single_workout_filter(wset, "erging", lambda km: km == 2),
        "6k": lambda wset: single_workout_filter(wset, "erging", lambda km: km == 6),
        "short_run": lambda wset: single_workout_filter(wset, "running", lambda km: km < 15),
        "long_run": lambda wset: single_workout_filter(wset, "running", lambda km: km > 15),
    }
    data = {}
    data["xs"] = {f"y_{k}": f"x_{k}" for k in series_map.keys()}
    data["axes"] = {
        "y_short_run": "y",
        "y_long_run": "y",
        "y_500m": "y2",
        "y_1000m": "y2",
        "y_2k": "y2",
        "y_6k": "y2",
    }
    columns = {f"y_{k}": [] for k in series_map.keys()}
    columns.update({f"x_{k}": [] for k in series_map.keys()})
    for day in days:
        series_key = None
        for key, test in series_map.items():
            if test(day.workout_set):
                series_key = key
        if series_key:
            columns[f"x_{series_key}"].append(day.day.strftime("%Y-%m-%d"))
            columns[f"y_{series_key}"].append(day.average_pace_seconds())
    data["types"] = {key: "spline" for key in columns.keys()}
    data["columns"] = [
        [label] + values
        for label, values in columns.items()
    ]

    return data
