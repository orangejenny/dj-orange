from datetime import datetime, timedelta
import random

from django.http import JsonResponse, HttpResponse
from django.template import loader
from django.views.decorators.http import require_GET


@require_GET
def days(request):
    template = loader.get_template('miles/days.html')
    days = [datetime.now()]
    while (len(days) < 21):
        days = [days[0] - timedelta(days=1)] + days
    context = {
        'days': days,
    }
    return HttpResponse(template.render(context, request))
