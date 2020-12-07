from collections import defaultdict
from datetime import datetime, timedelta

from django.contrib import messages
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
        # Saving a day
        try:
            date_string = "-".join([
                request.POST.get('year'),
                request.POST.get('month'),
                request.POST.get('day_of_month')
            ])
            date = datetime(
                int(request.POST.get('year')),
                int(request.POST.get('month')),
                int(request.POST.get('day_of_month'))
            )
        except ValueError as e:
            messages.error(request, f"Received invalid date {date_string}: " + str(e))
            return HttpResponse(render(request, "kilo/days.html"))
        day = Day.objects.filter(day=date).first()
        if day:
            if day.id != int(request.POST.get('day_id') or 0):
                messages.error(request, f"Attempting to duplicate {date_string}")
                return HttpResponse(render(request, "kilo/days.html"))
        else:
            day = Day()
        day.day = date
        day.notes = request.POST.get('notes')
        day.save()

        for workout in day.workout_set.all():
            if workout.id not in [int(i) for i in request.POST.getlist("workout_id") if i]:
                workout.delete()

        index = 0
        for workout_id in request.POST.getlist("workout_id"):
            workout = Workout.objects.get(id=int(workout_id)) if workout_id else Workout(day=day)
            for attr in ['activity', 'seconds', 'distance', 'distance_unit', 'sets', 'reps', 'weight']:
                setattr(workout, attr, request.POST.getlist(attr)[index] or None)
            if workout.activity:
                workout.save()
            index += 1

        messages.success(request, "Saved!")

    context = {
        "activity": activity,
        "distance_units": [u[0] for u in Workout.DISTANCE_UNITS],
        "activities": sorted(list({w.activity for d in Day.objects.all() for w in d.workout_set.all()})),
    }
    return HttpResponse(render(request, "kilo/days.html", context))


@require_GET
@login_required
def panel(request):
    activity = request.GET.get('activity')
    days = Day.objects.all()
    if activity:
        days = days.filter(workout__activity=activity).distinct()

    return JsonResponse({
        "recent_days": [_format_day(d) for d in days[:10]],
        "stats": _get_stats(days, activity),
        "graph_data": _get_graph_data(days, activity),
    })


def _format_day(day):
    return {
        "id": day.id,
        "day": day.day,
        "pretty_day": day.day.strftime("%a, %b %d, %Y"),
        "notes": day.notes,
        "workouts": [
            {
                "summary": w.summary,
                **w.to_json(),
            }
            for w in day.workout_set.all()
        ],
    }


def _get_stats(days, activity=None):
    today = datetime.now().date()
    last_month_days = days.filter(day__gte=today - timedelta(days=30))
    last_year_days = days.filter(day__gte=today - timedelta(days=365))

    if activity is None:
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
    data = {}

    if activity is None:
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
