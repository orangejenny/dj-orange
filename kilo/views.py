import json

from collections import defaultdict, Counter
from datetime import datetime, timedelta

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET

from kilo.models import Day, Workout
from kilo.stats import best_erg, best_run, sum_erging, sum_running


def days(request):
    return _days(request)


def days_erging(request):
    return _days(request, "erging")


def days_running(request):
    return _days(request, "running")


@login_required
def _days(request, activity=None):
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
            if workout.activity:
                workout.save()

        return JsonResponse({
            "success": 1,
            "day": day.to_json(),
        })

    return HttpResponse(render(request, "kilo/days.html"))


@require_GET
@login_required
def panel(request):
    activity = request.GET.get('activity')
    days = Day.objects.all()
    if activity:
        days = days.filter(workout__activity=activity).distinct()

    all_activities = [w.activity for d in Day.objects.all() for w in d.workout_set.all()]
    activity_counter = Counter(all_activities)
    common_activities = [a[0] for a in activity_counter.most_common(3)]
    other_activities = sorted({a for a in set(all_activities) if a not in common_activities})

    return JsonResponse({
        "all_activities": common_activities + other_activities,
        "all_distance_units": [u[0] for u in Workout.DISTANCE_UNITS],
        "recent_days": [_format_day(d) for d in days[:10]],
        "stats": _get_stats(days, activity),
        "graph_data": _get_graph_data(days, activity),
    })


def _format_day(day):
    return {
        "id": day.id,
        "day": day.day,
        "notes": day.notes,
        "workouts": [w.to_json() for w in day.workout_set.all()],
    }


def _get_stats(days, activity=None):
    today = datetime.now().date()
    last_month_days = days.filter(day__gte=today - timedelta(days=30))
    last_year_days = days.filter(day__gte=today - timedelta(days=365))

    if not activity:
        last_week_days = days.filter(day__gte=today - timedelta(days=7))
        text = "days/week"
        return [
            {"name": "Past Week", "primary": last_week_days.count(), "secondary": text},
            {"name": "Past Month", "primary": round(last_month_days.count() / 4.285, 1), "secondary": text},
            {"name": "Past Year", "primary": round(last_year_days.count() / 52, 1), "secondary": text},
        ]

    if activity == "erging":
        stats = [
            {"name": "Past Month", "primary": sum_erging(last_month_days), "secondary": "km erged"},
        ]
        workout = best_erg(last_month_days, km=2)
        if workout:
            stats.append({
                "name": "Past Month's Best 2k",
                "primary": workout.primary_stat(),
                "secondary": workout.secondary_stat(),
            })
        workout = best_erg(last_year_days, km=2)
        if workout:
            stats.append({
                "name": "Past Year's Best 2k",
                "primary": workout.primary_stat(),
                "secondary": workout.secondary_stat(),
            })
        workout = best_erg(last_month_days, km=6)
        if workout:
            stats.append({
                "name": "Past Month's Best 6k",
                "primary": workout.primary_stat(),
                "secondary": workout.secondary_stat(),
            })
        workout = best_erg(last_year_days, km=6)
        if workout:
            stats.append({
                "name": "Past Year's Best 6k",
                "primary": workout.primary_stat(),
                "secondary": workout.secondary_stat(),
            })
        return stats

    if activity == "running":
        stats = [{
            "name": "Past Month",
            "primary": sum_running(last_month_days),
            "secondary": "miles run",
        }]
        boundary = 7
        workout = best_run(last_month_days, upper_mi=boundary)
        if workout:
            stats.append({
                "name": "Past Month's Best Short Run",
                "primary": workout.primary_stat(),
                "secondary": workout.secondary_stat(),
            })
        workout = best_run(last_year_days, upper_mi=boundary)
        if workout:
            stats.append({
                "name": "Past Year's Best Short Run",
                "primary": workout.primary_stat(),
                "secondary": workout.secondary_stat(),
            })
        workout = best_run(last_month_days, lower_mi=boundary)
        if workout:
            stats.append({
                "name": "Past Month's Best Long Run",
                "primary": workout.primary_stat(),
                "secondary": workout.secondary_stat(),
            })
        workout = best_run(last_year_days, lower_mi=boundary)
        if workout:
            stats.append({
                "name": "Past Year's Best Long Run",
                "primary": workout.primary_stat(),
                "secondary": workout.secondary_stat(),
            })
        return stats

    return []


def _get_graph_data(days, activity=None):
    today = datetime.now().date()
    days = days.filter(day__gte=today - timedelta(days=30 if activity else 90))

    if not days.count():
        return None

    data = {}
    if not activity:
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
    else:
        (short_label, long_label) = ("2k", "6k") if activity == "erging" else ("short", "long")
        data["xs"] = {short_label: "x_short", long_label: "x_long"}
        columns = {"x_short": [], short_label: [], "x_long": [], long_label: []}
        boundary = 4 if activity == "erging" else 10
        for day in days:
            for workout in day.workout_set.all():
                if workout.activity == activity:
                    (x, y) = (None, None)
                    if workout.km <= boundary:
                        x = "x_short"
                        y = short_label
                    elif workout.km > boundary:
                        x = "x_long"
                        y = long_label
                    if x and y:
                        columns[x].append(day.day.strftime("%Y-%m-%d"))
                        columns[y].append(workout.seconds)
        data["types"] = {key: "spline" for key in columns.keys()}
        data["columns"] = [
            [label] + values
            for label, values in columns.items()
        ]

    return data
