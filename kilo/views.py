from datetime import datetime, timedelta

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.template import loader
from django.views.decorators.http import require_GET

from kilo.models import Day, Workout


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
    if activity:
        days = days.filter(workout__activity=activity).distinct()

    stats = _get_stats(days, activity)

    return JsonResponse({
        "recent_days": [_format_day(d) for d in days[:10]],
        "stats": stats,
    })


def _format_day(day):
    return {
        "day": str(day.day),
        "notes": day.notes,
        "workouts": [
            {
                "activity": w.activity,
            } for w in day.workout_set.all()
        ],
    }


def _get_stats(days, activity=None):
    today = datetime.now().date()
    last_week_days = days.filter(day__gte=today - timedelta(days=7))
    last_month_days = days.filter(day__gte=today - timedelta(days=30))
    last_year_days = days.filter(day__gte=today - timedelta(days=365))

    if activity is None:
        text = "days/week"
        return [
            {"name": "Past Week", "primary": last_week_days.count(), "secondary": text},
            {"name": "Past Month", "primary": round(last_month_days.count() / 4.285, 1), "secondary": text},
            {"name": "Past Year", "primary": round(last_year_days.count() / 52, 1), "secondary": text},
        ]

    if activity == "erging":
        stats = [
            {"name": "Past Month", "primary": _sum_erging(last_month_days), "secondary": "km erged"},
        ]
        workout = _best_erg(last_month_days, km=2)
        if workout:
            stats.append({"name": "Past Month's Best 2k", "primary": workout.primary_stat(), "secondary": workout.secondary_stat()})
        workout = _best_erg(last_year_days, km=2)
        if workout:
            stats.append({"name": "Past Year's Best 2k", "primary": workout.primary_stat(), "secondary": workout.secondary_stat()})
        workout = _best_erg(last_month_days, km=6)
        if workout:
            stats.append({"name": "Past Month's Best 6k", "primary": workout.primary_stat(), "secondary": workout.secondary_stat()})
        workout = _best_erg(last_year_days, km=6)
        if workout:
            stats.append({"name": "Past Year's Best 6k", "primary": workout.primary_stat(), "secondary": workout.secondary_stat()})
        return stats

    if activity == "running":
        stats = [
            {"name": "Past Month", "primary": _sum_running(last_month_days), "secondary": "miles run"},
        ]
        boundary = 7
        workout = _best_run(last_month_days, upper_mi=boundary)
        if workout:
            stats.append({"name": "Past Month's Best Short Run", "primary": workout.primary_stat(), "secondary": workout.secondary_stat()})
        workout = _best_run(last_year_days, upper_mi=boundary)
        if workout:
            stats.append({"name": "Past Year's Best Short Run", "primary": workout.primary_stat(), "secondary": workout.secondary_stat()})
        workout = _best_run(last_month_days, lower_mi=boundary)
        if workout:
            stats.append({"name": "Past Month's Best Long Run", "primary": workout.primary_stat(), "secondary": workout.secondary_stat()})
        workout = _best_run(last_year_days, lower_mi=boundary)
        if workout:
            stats.append({"name": "Past Year's Best Long Run", "primary": workout.primary_stat(), "secondary": workout.secondary_stat()})
        return stats

    return []


def _sum_erging(days):
    total = 0
    for day in days:
        for workout in day.workout_set.all():
            if workout.activity == "erging":
                total += workout.m or 0
    return "{:,}".format(round(total))


def _sum_running(days):
    total = 0
    for day in days:
        for workout in day.workout_set.all():
            if workout.activity == "running":
                total += workout.mi or 0
    return "{:,}".format(round(total))


def _best_erg(days, km):
    best = None
    for day in days:
        for workout in day.workout_set.all():
            if workout.activity == "erging" and workout.km == km:
                if best is None or workout.faster_than(best):
                    best = workout
    return best


def _best_run(days, lower_mi=None, upper_mi=None):
    best = None
    for day in days:
        for workout in day.workout_set.all():
            if workout.activity == "running":
                if lower_mi is None or workout.mi >= lower_mi:
                    if upper_mi is None or workout.mi <= upper_mi:
                        if best is None or workout.faster_than(best):
                            best = workout
    return best
