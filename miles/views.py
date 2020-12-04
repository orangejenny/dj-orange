from datetime import datetime, timedelta

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.template import loader
from django.views.decorators.http import require_GET

from miles.models import Day


@require_GET
@login_required
def days(request):
    template = loader.get_template('miles/days.html')
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
            {"name": "This Week", "primary": last_week_days.count(), "secondary": text},
            {"name": "This Month", "primary": round(last_month_days.count() / 4.285, 1), "secondary": text},
            {"name": "This Year", "primary": round(last_year_days.count() / 52, 1), "secondary": text},
        ]

    if activity == "erging":
        return []

    if activity == "running":
        return []
