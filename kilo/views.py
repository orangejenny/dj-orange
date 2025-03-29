import json

from collections import defaultdict
from datetime import datetime, timedelta

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET, require_POST

from kilo.models import Day, Workout
from kilo.stats import best_erg, best_run, sum_erging, sum_running


@login_required
def base(request):
    return HttpResponse(render(request, "kilo/base.html"))


@require_POST
@login_required
def update(request):
    date_obj = datetime(
        int(request.POST.get('year')),
        int(request.POST.get('month')),
        int(request.POST.get('day_of_month')),
    )

    day = Day.objects.filter(day=date_obj).first()
    if day is None:
        day = Day(day=date_obj)
    day.notes = request.POST.get('notes')
    day.save()

    return render(request, "kilo/partials/day_row.html", {
        "day": _format_day(day),
        "all_activities": Workout.activity_options(),
        "all_distance_units": Workout.DISTANCE_UNITS,
    })


@require_POST
@login_required
def add_workout(request):
    date_obj = datetime(
        int(request.POST.get('year')),
        int(request.POST.get('month')),
        int(request.POST.get('day_of_month')),
    )

    day = Day.objects.filter(day=date_obj).first()
    if day is None:
        day = Day(day=date_obj)
        day.save()

    workout = Workout(day=day)
    workout.activity = "running"
    workout.save()

    return render(request, "kilo/partials/workout_item.html", {
        "workout": workout.to_json(),
        "all_activities": Workout.activity_options(),
        "all_distance_units": Workout.DISTANCE_UNITS,
    })


@require_POST
@login_required
def delete_workout(request):
    workout = Workout.objects.get(id=int(request.POST.get('workout_id')))
    workout.delete()
    return HttpResponse("")


@require_POST
@login_required
def update_workout(request):
    workout = Workout.objects.get(id=request.POST.get('workout_id'))

    for cast, attrs in [
        (str, ['activity', 'distance_unit']),
        (int, ['seconds', 'sets', 'reps']),
        (float, ['distance', 'weight']),
    ]:
        for attr in attrs:
            if request.POST.get(attr):
                setattr(workout, attr, cast(request.POST.get(attr)))

    time = request.POST.get('time')
    if time:
        workout.seconds = Workout.parse_time(time)

    workout.save()

    return render(request, "kilo/partials/workout_item.html", {
        "workout": workout.to_json(),
        "all_activities": Workout.activity_options(),
        "all_distance_units": Workout.DISTANCE_UNITS,
    })


@require_GET
@login_required
def recent(request):
    today = datetime.now().date()
    all_days = []

    for delta in range(0, 15):
        day_index = today - timedelta(days=delta)
        days = Day.objects.filter(day=day_index)
        if not days:
            days = [Day(day=day_index)]
        all_days.extend([d for d in days])

    return _days(request, all_days)


@require_GET
@login_required
def history(request):
    days = Day.get_recent_days(90)
    return _days(request, days)


def _days(request, days):

    return render(request, "kilo/partials/days_table.html", {
        "days": [_format_day(d) for d in days],
        "all_activities": Workout.activity_options(),
        "all_distance_units": Workout.DISTANCE_UNITS,
    })


def _format_day(day):
    return {
        "id": day.id,
        "day": day.day,
        "year": day.day.year,
        "month": day.day.month,
        "month_name": ['', 'Jan', 'Feb', 'March', 'April', 'May', 'June', 'July', 'Aug', 'Sept', 'Oct', 'Nov', 'Dec'][day.day.month],
        "day_of_month": day.day.day,
        "day_of_week": ['Mon', 'Tues', 'Wed', 'Thurs', 'Fri', 'Sat', 'Sun'][day.day.weekday()],
        "notes": day.notes,
        "workouts": [w.to_json() for w in day.workout_set.all()] if day.id else [],
    }


@require_GET
@login_required
def stats(request):
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

    return render(request, "kilo/partials/stats.html", {
        "stats": [{
            "title": "Erging",
            "stats": erging_stats,
        }, {
            "title": "Running",
            "stats": running_stats,
        }],
    })


@require_GET
@login_required
def frequency(request):
    days = Day.get_recent_days(365)

    data = {}
    data["x"] = "day"
    all_activities = {d.primary_activity for d in days if d.primary_activity}
    day_series = []
    series = defaultdict(list)
    index = days.last().day
    while index <= datetime.now().date():
        day_series.append(index.strftime("%Y-%m-%d"))
        next_index = index + timedelta(days=7)
        activity_counts = defaultdict(lambda: 0)
        for day in days.filter(day__gte=index, day__lt=next_index):
            activity_counts[day.primary_activity] += 1
        for activity in all_activities:
            series[activity].append(activity_counts[activity] or 0)
        index = next_index
    data["columns"] = [["day"] + day_series] + [
        [activity] + counts
        for activity, counts in series.items()
    ]
    data["types"] = {activity: "area-spline" for activity in all_activities}
    data["groups"] = [list(all_activities)]
    options = _get_graph_options(data)
    options.update({
        "legend": {"show": True},
        "point": {"show": False},
        "tooltip": {
            "show": False,
            "grouped": False,
        },
    })
    options["axis"]["y"]["max"] = 7
    options["axis"]["y"]["tick"] = {"count": 8}
    return JsonResponse(options)


@require_GET
@login_required
def pace(request):
    days = Day.get_recent_days(365)

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
    options = _get_graph_options(data)
    options.update({
        "legend": {"show": False},
        "point": {"show": True},
        "tooltip": {
            "show": True,
            "grouped": False,
        },
    })
    options["axis"]["y"]["min"] = 0 * 60
    options["axis"]["y"]["max"] = 11 * 60
    options["axis"]["y"]["tick"] = {
        "outer": False,
        #"format": self.getTime,    # TODO
        "values": [x * 60 for x in [7, 8, 9, 10]],
    }
    options["axis"]["y2"] = {
        "show": True,
        "min": 1.75 * 60,
        "max": 2.5 * 60,
        "tick": {
            "outer": False,
            #"format": self.getTime,    # TODO
            "values": [105, 110, 115, 120, 125, 130, 135],
        },
    }
    return JsonResponse(options)


def _get_graph_options(data):
    return {
        "bindto": "#panel",
        "data": data,
        "axis": {
            "x": {
                "type": "timeseries",
                "tick": {
                    "count": len(data["columns"][0]),
                    "fit": True,
                    "format": "%b %d",
                    "rotate": 90,
                },
            },
            "y": {
                "min": 0,
                "padding": {
                    "top": 0,
                    "bottom": 0,
                },
            },
        },
    }
