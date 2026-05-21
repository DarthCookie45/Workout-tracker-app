from django.shortcuts import render, redirect, get_object_or_404
from .models import Workout
from .forms import WorkoutForm
from collections import defaultdict
import json
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib import messages

# Create your views here.
# Homepage / Dashboard
@login_required
def home(request):
    workouts = Workout.objects.filter(
        user=request.user
    ).order_by('-workout_date')

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

    heaviest_lift = max(
    [float(workout.weight) for workout in workouts],
    default=0
)

    recent_workouts = workouts[:5]

    muscle_group_counts = defaultdict(int)

    for workout in workouts:
        muscle_group_counts[workout.muscle_group] += 1

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
        'heaviest_lift': heaviest_lift,
        'muscle_group_counts': dict(muscle_group_counts),
    }

    return render(request, 'tracker/home.html', context)

@login_required
def workout_detail(request, workout_id):
    workout = get_object_or_404(
        Workout,
        id=workout_id,
        user=request.user
    )

    context = {
        'workout': workout
    }

    return render(
        request,
        'tracker/workout_detail.html',
        context
    )


# Add workout
@login_required
def add_workout(request):
    if request.method == "POST":
        form = WorkoutForm(request.POST)

        if form.is_valid():
            workout = form.save(commit=False)
            workout.user = request.user
            workout.save()
            messages.success(request, 'Workout added successfully!')
            return redirect('home')

    else:
        form = WorkoutForm()

    return render(
        request,
        'tracker/add_workout.html',
        {'form': form}
    )


# Edit workout
@login_required
def edit_workout(request, workout_id):
    workout = get_object_or_404(
    Workout,
    id=workout_id,
    user=request.user
)

    if request.method == 'POST':
        form = WorkoutForm(
            request.POST,
            instance=workout
        )

        if form.is_valid():
            form.save()
            messages.success(request, 'Workout updated successfully!')
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
@login_required
def delete_workout(request, workout_id):
    workout = get_object_or_404(
    Workout,
    id=workout_id,
    user=request.user
)

    if request.method == 'POST':
        workout.delete()
        messages.success(request, 'Workout deleted successfully!')
        return redirect('home')

    context = {
        'workout': workout
    }

    return render(
        request,
        'tracker/delete_workout.html',
        context
    )

# User registration
def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')

    else:
        form = UserCreationForm()

    return render(
        request,
        'tracker/register.html',
        {'form': form}
    )