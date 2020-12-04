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
            {"name": "Past Month", "primary": _sum_meters(last_month_days), "secondary": "km erged"},
        ]
        workout = _best_erg(last_month_days, km=2)
        if workout:
            stats.append({"name": "Past Month's Best 2k", "primary": workout.pace, "secondary": workout.day.day})
        workout = _best_erg(last_year_days, km=2)
        if workout:
            stats.append({"name": "Past Year's Best 2k", "primary": workout.pace, "secondary": workout.day.day})
        workout = _best_erg(last_month_days, km=6)
        if workout:
            stats.append({"name": "Past Month's Best 6k", "primary": workout.pace, "secondary": workout.day.day})
        workout = _best_erg(last_year_days, km=6)
        if workout:
            stats.append({"name": "Past Year's Best 6k", "primary": workout.pace, "secondary": workout.day.day})
        return stats

    if activity == "running":
        return []


def _sum_meters(days):
    sum = 0
    for day in days:
        for workout in day.workout_set.all():
            if workout.activity == "erging":
                sum += workout.m or 0
    return "{:,}".format(round(sum))


def _best_erg(days, km):
    best = None
    for day in days:
        for workout in day.workout_set.all():
            if workout.activity == "erging" and workout.km == km:
                if best is None or workout.seconds < best.seconds:
                    best = workout
    return best
