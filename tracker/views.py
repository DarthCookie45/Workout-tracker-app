from django.shortcuts import render, redirect, get_object_or_404
from .models import Workout, WorkoutRoutine, Exercise
from .forms import WorkoutForm, WorkoutRoutineForm, ExerciseForm
from collections import defaultdict
import json
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib import messages
import requests
from django.conf import settings

# Create your views here.
# Homepage / Dashboard
def home(request):
    if request.user.is_authenticated:
        workouts = Workout.objects.filter(
            user=request.user
        ).order_by('-workout_date')
    else:
        workouts = Workout.objects.none()

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

# Workouts
@login_required
def workouts(request):
    routines = WorkoutRoutine.objects.filter(
        user=request.user
    ).order_by('-workout_date')

    context = {
        'routines': routines
    }

    return render(
        request,
        'tracker/workouts.html',
        context
    )

# Progress view
@login_required
def progress(request):
    routines = WorkoutRoutine.objects.filter(user=request.user)
    exercises = Exercise.objects.filter(routine__user=request.user)

    total_routines = routines.count()
    total_exercises = exercises.count()

    total_sets = sum(exercise.sets for exercise in exercises)

    total_volume = sum(
        float(exercise.weight) * exercise.sets
        for exercise in exercises
    )

    heaviest_lift = max(
        [float(exercise.weight) for exercise in exercises],
        default=0
    )

    volume_labels = []
    volume_data = []

    for routine in routines:
        routine_volume = sum(
            float(exercise.weight) * exercise.sets
            for exercise in routine.exercises.all()
        )

    volume_labels.append(routine.name)
    volume_data.append(routine_volume)

    context = {
        'total_routines': total_routines,
        'total_exercises': total_exercises,
        'total_sets': total_sets,
        'total_volume': total_volume,
        'heaviest_lift': heaviest_lift,
        'volume_labels': json.dumps(volume_labels),
        'volume_data': json.dumps(volume_data),
        'volume_labels': json.dumps(volume_labels),
        'volume_data': json.dumps(volume_data),
    }

    return render(
        request,
        'tracker/progress.html',
        context
    )

# Calendar view
@login_required
def calendar(request):
    return render(
        request,
        'tracker/calendar.html'
    )

# profile view
@login_required
def profile(request):
    return render(
        request,
        'tracker/profile.html'
    )

# View workout details
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

# Add workout routine
@login_required
def add_routine(request):
    if request.method == "POST":
        form = WorkoutRoutineForm(request.POST)

        if form.is_valid():
            routine = form.save(commit=False)
            routine.user = request.user
            routine.save()
            messages.success(request, "Workout routine added successfully.")
            return redirect('workouts')

    else:
        form = WorkoutRoutineForm()

    return render(
        request,
        'tracker/add_routine.html',
        {'form': form}
    )

# View routine
@login_required
def routine_detail(request, routine_id):
    routine = get_object_or_404(
        WorkoutRoutine,
        id=routine_id,
        user=request.user
    )

    exercises = routine.exercises.all()

    context = {
        'routine': routine,
        'exercises': exercises,
    }

    return render(
        request,
        'tracker/routine_detail.html',
        context
    )

# Add exercise
@login_required
def add_exercise(request, routine_id):
    routine = get_object_or_404(
        WorkoutRoutine,
        id=routine_id,
        user=request.user
    )

    if request.method == "POST":
        form = ExerciseForm(request.POST)

        if form.is_valid():
            exercise = form.save(commit=False)
            exercise.routine = routine
            exercise.save()
            messages.success(request, "Exercise added successfully.")
            return redirect('routine_detail', routine_id=routine.id)

    else:
        initial_data = {
            'name': request.GET.get('name', '')
        }

        form = ExerciseForm(initial=initial_data)

    return render(
        request,
        'tracker/add_exercise.html',
        {
            'form': form,
            'routine': routine
        }
    )

# Edit exercise
@login_required
def edit_exercise(request, exercise_id):
    exercise = get_object_or_404(
        Exercise,
        id=exercise_id,
        routine__user=request.user
    )

    routine = exercise.routine

    if request.method == "POST":
        form = ExerciseForm(
            request.POST,
            instance=exercise
        )

        if form.is_valid():
            form.save()
            messages.success(request, "Exercise updated successfully.")
            return redirect('routine_detail', routine_id=routine.id)

    else:
        form = ExerciseForm(instance=exercise)

    return render(
        request,
        'tracker/edit_exercise.html',
        {
            'form': form,
            'routine': routine
        }
    )

# Delete exercise
@login_required
def delete_exercise(request, exercise_id):
    exercise = get_object_or_404(
        Exercise,
        id=exercise_id,
        routine__user=request.user
    )

    routine = exercise.routine

    if request.method == "POST":
        exercise.delete()
        messages.success(request, "Exercise deleted successfully.")
        return redirect('routine_detail', routine_id=routine.id)

    return render(
        request,
        'tracker/delete_exercise.html',
        {
            'exercise': exercise,
            'routine': routine
        }
    )

# Edit routine
@login_required
def edit_routine(request, routine_id):
    routine = get_object_or_404(
        WorkoutRoutine,
        id=routine_id,
        user=request.user
    )

    if request.method == "POST":
        form = WorkoutRoutineForm(
            request.POST,
            instance=routine
        )

        if form.is_valid():
            form.save()
            messages.success(request, "Workout routine updated successfully.")
            return redirect('workouts')

    else:
        form = WorkoutRoutineForm(instance=routine)

    return render(
        request,
        'tracker/edit_routine.html',
        {
            'form': form,
            'routine': routine
        }
    )

# Delete routine
@login_required
def delete_routine(request, routine_id):
    routine = get_object_or_404(
        WorkoutRoutine,
        id=routine_id,
        user=request.user
    )

    if request.method == "POST":
        routine.delete()
        messages.success(request, "Workout routine deleted successfully.")
        return redirect('workouts')

    return render(
        request,
        'tracker/delete_routine.html',
        {'routine': routine}
    )

# Exercise library view with API integration
@login_required
def exercise_library(request, routine_id):
    routine = get_object_or_404(
        WorkoutRoutine,
        id=routine_id,
        user=request.user
    )
    

    exercise_name = request.GET.get('name', '')
    muscle = request.GET.get('muscle', '')
    difficulty = request.GET.get('difficulty', '')

    exercises = []
    api_error = None

    if exercise_name or muscle:
        api_url = 'https://api.api-ninjas.com/v1/exercises'

        params = {}

        if exercise_name:
            params['name'] = exercise_name

        if muscle:
            params['muscle'] = muscle

        if difficulty:
            params['difficulty'] = difficulty

        try:
            response = requests.get(
                api_url,
                headers={'X-Api-Key': settings.API_NINJAS_KEY},
                params=params,
                timeout=5
            )

            if response.status_code == 200:
                exercises = response.json()
            else:
                api_error = "Exercise library is unavailable right now."

        except requests.RequestException:
            api_error = "Exercise library could not be reached. You can still add exercises manually."

    context = {
        'routine': routine,
        'exercises': exercises,
        'exercise_name': exercise_name,
        'muscle': muscle,
        'difficulty': difficulty,
        'api_error': api_error,
    }

    return render(
        request,
        'tracker/exercise_library.html',
        context
    )