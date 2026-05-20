from django.shortcuts import render, redirect
from .models import Workout
from .forms import WorkoutForm
from collections import defaultdict
import json

# Create your views here.
# Homepage / Dashboard
def home(request):
    workouts = Workout.objects.all().order_by('-workout_date')

    search_query = request.GET.get('search', '')
    filter_option = request.GET.get('filter', '')
    muscle_group = request.GET.get('muscle_group', '')

    # Search filtering
    if search_query:
        workouts = workouts.filter(
            workout_name__icontains=search_query
        )

    # Muscle group filtering
    if muscle_group:
        workouts = workouts.filter(
            muscle_group=muscle_group
        )

    # Workout ordering filters
    if filter_option == 'oldest':
        workouts = workouts.order_by('workout_date')

    elif filter_option == 'newest':
        workouts = workouts.order_by('-workout_date')

    elif filter_option == 'highest_volume':
        workouts = sorted(
            workouts,
            key=lambda workout: (
                float(workout.weight) * workout.sets * workout.reps
            ),
            reverse=True
        )

    # Dashboard statistics
    total_workouts = len(workouts)

    total_sets = sum(
        workout.sets for workout in workouts
    )

    total_weight = sum(
        float(workout.weight) * workout.sets * workout.reps
        for workout in workouts
    )

    recent_workouts = workouts[:5]

    # Workout volume chart data grouped by muscle group
    volume_data = defaultdict(float)

    for workout in workouts:
        volume = (
            float(workout.weight)
            * workout.reps
            * workout.sets
        )

        volume_data[workout.muscle_group] += volume

    chart_labels = json.dumps(list(volume_data.keys()))
    chart_data = json.dumps(list(volume_data.values()))

    context = {
        'workouts': workouts,
        'total_workouts': total_workouts,
        'total_sets': total_sets,
        'total_weight': total_weight,
        'recent_workouts': recent_workouts,
        'search_query': search_query,
        'filter_option': filter_option,
        'muscle_group': muscle_group,
        'chart_labels': chart_labels,
        'chart_data': chart_data,
    }

    return render(request, 'tracker/home.html', context)


# Add workout
def add_workout(request):
    if request.method == "POST":
        form = WorkoutForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('home')

    else:
        form = WorkoutForm()

    return render(
        request,
        'tracker/add_workout.html',
        {'form': form}
    )


# Edit workout
def edit_workout(request, workout_id):
    workout = Workout.objects.get(id=workout_id)

    if request.method == 'POST':
        form = WorkoutForm(
            request.POST,
            instance=workout
        )

        if form.is_valid():
            form.save()
            return redirect('home')

    else:
        form = WorkoutForm(instance=workout)

    context = {
        'form': form
    }

    return render(
        request,
        'tracker/edit_workout.html',
        context
    )


# Delete workout
def delete_workout(request, workout_id):
    workout = Workout.objects.get(id=workout_id)

    if request.method == 'POST':
        workout.delete()
        return redirect('home')

    context = {
        'workout': workout
    }

    return render(
        request,
        'tracker/delete_workout.html',
        context
    )