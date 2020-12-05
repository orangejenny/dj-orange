from kilo.models import Workout


def sum_erging(days):
    total = 0
    for day in days:
        for workout in day.workout_set.all():
            if workout.activity == "erging":
                total += workout.m or 0
    return "{:,}".format(round(total))


def sum_running(days):
    total = 0
    for day in days:
        for workout in day.workout_set.all():
            if workout.activity == "running":
                total += workout.mi or 0
    return "{:,}".format(round(total))


def best_erg(days, km):
    best = None
    for day in days:
        for workout in day.workout_set.all():
            if workout.activity == "erging" and workout.km == km:
                if best is None or workout.faster_than(best):
                    best = workout
    return best


def best_run(days, lower_mi=None, upper_mi=None):
    best = None
    for day in days:
        for workout in day.workout_set.all():
            if workout.activity == "running" and workout.mi and workout.seconds:
                if lower_mi is None or workout.mi >= lower_mi:
                    if upper_mi is None or workout.mi <= upper_mi:
                        if best is None or workout.faster_than(best):
                            best = workout
    return best
