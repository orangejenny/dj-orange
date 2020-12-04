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

    return JsonResponse({
        "recent_days": [_format_day(d) for d in days[:10]],
        "stats": [
            {"name": "first", "primary": 1.2, "secondary": 1.3},
            {"name": "first", "primary": 1.2, "secondary": 1.3},
        ],
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
