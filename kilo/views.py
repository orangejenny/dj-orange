from collections import defaultdict
from datetime import datetime, timedelta

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.template import loader
from django.views.decorators.http import require_GET

from kilo.models import Day
from kilo.stats import best_erg, best_run, sum_erging, sum_running


@require_GET
@login_required
def days(request):
    template = loader.get_template('kilo/days.html')
    context = {}
    return HttpResponse(template.render(context, request))


@require_GET
@login_required
def panel(request):
    activity = request.GET.get('activity')
    days = Day.objects.all()

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
            stats.append({"name": "Past Month's Best 2k", "primary": workout.primary_stat(), "secondary": workout.secondary_stat()})
        workout = best_erg(last_year_days, km=2)
        if workout:
            stats.append({"name": "Past Year's Best 2k", "primary": workout.primary_stat(), "secondary": workout.secondary_stat()})
        workout = best_erg(last_month_days, km=6)
        if workout:
            stats.append({"name": "Past Month's Best 6k", "primary": workout.primary_stat(), "secondary": workout.secondary_stat()})
        workout = best_erg(last_year_days, km=6)
        if workout:
            stats.append({"name": "Past Year's Best 6k", "primary": workout.primary_stat(), "secondary": workout.secondary_stat()})
        return stats

    if activity == "running":
        stats = [
            {"name": "Past Month", "primary": sum_running(last_month_days), "secondary": "miles run"},
        ]
        boundary = 7
        workout = best_run(last_month_days, upper_mi=boundary)
        if workout:
            stats.append({"name": "Past Month's Best Short Run", "primary": workout.primary_stat(), "secondary": workout.secondary_stat()})
        workout = best_run(last_year_days, upper_mi=boundary)
        if workout:
            stats.append({"name": "Past Year's Best Short Run", "primary": workout.primary_stat(), "secondary": workout.secondary_stat()})
        workout = best_run(last_month_days, lower_mi=boundary)
        if workout:
            stats.append({"name": "Past Month's Best Long Run", "primary": workout.primary_stat(), "secondary": workout.secondary_stat()})
        workout = best_run(last_year_days, lower_mi=boundary)
        if workout:
            stats.append({"name": "Past Year's Best Long Run", "primary": workout.primary_stat(), "secondary": workout.secondary_stat()})
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
        data["xs"] = {"y_short": "x_short", "y_long": "x_long"}
        columns = {"x_short": [], "y_short": [], "x_long": [], "y_long": []}
        boundary = 4 if activity == "erging" else 10
        for day in days:
            for workout in day.workout_set.all():
                if workout.activity == activity:
                    (x, y) = (None, None)
                    if workout.km <= boundary:
                        x = "x_short"
                        y = "y_short"
                    elif workout.km > boundary:
                        x = "x_long"
                        y = "y_long"
                    if x and y:
                        columns[x].append(day.day.strftime("%Y-%m-%d"))
                        columns[y].append(workout.seconds)
        data["types"] = {key: "spline" for key in columns.keys()}
        data["columns"] = [
            [label] + values
            for label, values in columns.items()
        ]

    return data
