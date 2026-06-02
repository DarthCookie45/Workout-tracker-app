from django.shortcuts import render, redirect, get_object_or_404
from .models import Workout, WorkoutRoutine, Exercise, Profile
from .forms import WorkoutForm, WorkoutRoutineForm, ExerciseForm
from collections import defaultdict
import json
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm
from django.contrib.auth import login, update_session_auth_hash
from django.contrib import messages
import requests
from django.conf import settings
import calendar as calendar_module
from datetime import date, datetime, timedelta
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash

# Create your views here.
# Homepage / Dashboard
def home(request):
    if request.user.is_authenticated:
        routines = WorkoutRoutine.objects.filter(
            user=request.user
        ).order_by('-workout_date')

        exercises = Exercise.objects.filter(
            routine__user=request.user
        )

        next_workout = WorkoutRoutine.objects.filter(
            user=request.user,
            workout_date__gte=date.today()
        ).order_by('workout_date').first()

    else:
        routines = WorkoutRoutine.objects.none()
        exercises = Exercise.objects.none()
        next_workout = None

    total_workouts = routines.count()
    total_exercises = exercises.count()

    total_sets = sum(
        exercise.sets for exercise in exercises
    )

    active_days = routines.values(
        'workout_date'
    ).distinct().count()

    total_weight = sum(
        float(exercise.weight) * exercise.sets
        for exercise in exercises
    )

    heaviest_lift = max(
        [float(exercise.weight) for exercise in exercises],
        default=0
    )

    recent_workouts = routines[:5]

    volume_data = defaultdict(float)

    for routine in routines:
        routine_volume = sum(
            float(exercise.weight) * exercise.sets
            for exercise in routine.exercises.all()
        )

        volume_data[routine.name] += routine_volume

    chart_labels = json.dumps(list(volume_data.keys()))
    chart_data = json.dumps(list(volume_data.values()))

    context = {
        'routines': routines,
        'exercises': exercises,
        'total_workouts': total_workouts,
        'total_exercises': total_exercises,
        'total_sets': total_sets,
        'active_days': active_days,
        'total_weight': total_weight,
        'heaviest_lift': heaviest_lift,
        'recent_workouts': recent_workouts,
        'chart_labels': chart_labels,
        'chart_data': chart_data,
        "next_workout": next_workout,
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
    exercises = Exercise.objects.filter(
        routine__user=request.user
    ).order_by('routine__workout_date')

    exercise_names = (
        exercises
        .values_list('name', flat=True)
        .distinct()
        .order_by('name')
    )

    selected_exercise = request.GET.get('exercise', '')

    if not selected_exercise and exercise_names:
        selected_exercise = exercise_names[0]

    selected_exercises = exercises.filter(
        name=selected_exercise
    )

    pb_weight = max(
        [float(exercise.weight) for exercise in selected_exercises],
        default=0
    )

    pb_record = None

    for exercise in selected_exercises:
        if float(exercise.weight) == pb_weight:
            pb_record = exercise
            break

    chart_labels = []
    chart_data = []

    for exercise in selected_exercises:
        chart_labels.append(
            exercise.routine.workout_date.strftime("%d %b")
        )

        chart_data.append(
            float(exercise.weight)
        )

    total_routines = routines.count()
    total_exercises = exercises.count()
    total_sets = sum(exercise.sets for exercise in exercises)

    personal_bests = 0

    for name in exercise_names:
        name_exercises = exercises.filter(name=name)

        if name_exercises.exists():
            personal_bests += 1

    context = {
        'total_routines': total_routines,
        'total_exercises': total_exercises,
        'total_sets': total_sets,
        'personal_bests': personal_bests,
        'exercise_names': exercise_names,
        'selected_exercise': selected_exercise,
        'pb_weight': pb_weight,
        'pb_record': pb_record,
        'chart_labels': json.dumps(chart_labels),
        'chart_data': json.dumps(chart_data),
    }

    return render(
        request,
        'tracker/progress.html',
        context
    )

# Calendar view
@login_required
def calendar(request):
    today = date.today()

    year = int(request.GET.get('year', today.year))
    month = int(request.GET.get('month', today.month))

    previous_month = month - 1
    previous_year = year

    if previous_month == 0:
        previous_month = 12
        previous_year -= 1

    next_month = month + 1
    next_year = year

    if next_month == 13:
        next_month = 1
        next_year += 1

    calendar_view = request.GET.get('view', 'month')

    week_date = request.GET.get("date")

    if week_date:
        selected_date = datetime.strptime(
            week_date,
            "%Y-%m-%d"
        ).date()
    else:
        selected_date = date(year, month, 1)

    week_start = selected_date - timedelta(days=selected_date.weekday())

    week_days = [
        week_start + timedelta(days=i)
        for i in range(7)
    ]

    week_label = f"{week_start.strftime('%d %b')} - {week_days[-1].strftime('%d %b %Y')}"

    previous_week = week_start - timedelta(days=7)
    next_week = week_start + timedelta(days=7)

    if calendar_view == 'week':
        routines = WorkoutRoutine.objects.filter(
        user=request.user,
        workout_date__gte=week_start,
        workout_date__lte=week_days[-1]
        ).order_by('workout_date')

    else:
        routines = WorkoutRoutine.objects.filter(
        user=request.user,
        workout_date__year=year,
        workout_date__month=month
        ).order_by('workout_date')

    month_calendar = calendar_module.Calendar(firstweekday=0).monthdatescalendar(
        year,
        month
    )

    routine_lookup = {}

    for routine in routines:
        routine_lookup.setdefault(
            routine.workout_date,
            []
        ).append(routine)

    context = {
        'month_calendar': month_calendar,
        'routine_lookup': routine_lookup,
        'month_name': calendar_module.month_name[month],
        'year': year,
        'month': month,
        'today': today,
        'previous_month': previous_month,
        'previous_year': previous_year,
        'next_month': next_month,
        'next_year': next_year,
        'today_month': today.month,
        'today_year': today.year,
        'calendar_view': calendar_view,
        'routines': routines,
        'week_days': week_days,
        'previous_week_date': previous_week.strftime("%Y-%m-%d"),
        'next_week_date': next_week.strftime("%Y-%m-%d"),
        'week_label': week_label,
        'today_date': today.strftime("%Y-%m-%d"),
    }

    return render(
        request,
        'tracker/calendar.html',
        context
    )

# profile view
@login_required
def profile(request):
    routines = WorkoutRoutine.objects.filter(
        user=request.user
    )

    exercises = Exercise.objects.filter(
        routine__user=request.user
    )

    profile, created = Profile.objects.get_or_create(
        user=request.user
    )

    total_routines = routines.count()
    total_exercises = exercises.count()

    total_sets = sum(
        exercise.sets for exercise in exercises
    )

    total_volume = sum(
        float(exercise.weight) * exercise.sets
        for exercise in exercises
    )

    personal_bests = (
        exercises
        .values_list('name', flat=True)
        .distinct()
        .count()
    )

    password_form = PasswordChangeForm(user=request.user)

    if request.method == "POST":
        form_type = request.POST.get("form_type")

        if form_type == "profile":
            email = request.POST.get("email", "").strip()
            bodyweight = request.POST.get("bodyweight", "").strip()

            request.user.email = email
            request.user.save()

            profile.bodyweight = bodyweight or None
            profile.save()

            messages.success(request, "Profile updated successfully.")
            return redirect("profile")

        if form_type == "password":
            password_form = PasswordChangeForm(
                user=request.user,
                data=request.POST
            )

            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Password changed successfully.")
                return redirect("profile")
            else:
                messages.warning(
                    request,
                    "Password could not be changed. Please check the errors below."
                )

    context = {
        'total_routines': total_routines,
        'total_exercises': total_exercises,
        'total_sets': total_sets,
        'total_volume': total_volume,
        'personal_bests': personal_bests,
        'password_form': password_form,
        'profile': profile,
    }

    return render(
        request,
        'tracker/profile.html',
        context
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
        form = CustomUserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')

    else:
        form = CustomUserCreationForm()

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

    personal_best_ids = []

    for exercise in exercises:
        best_weight = Exercise.objects.filter(
            routine__user=request.user,
            name__iexact=exercise.name
        ).order_by('-weight').first()

        if best_weight and exercise.weight == best_weight.weight:
            personal_best_ids.append(exercise.id)

    context = {
        'routine': routine,
        'exercises': exercises,
        'personal_best_ids': personal_best_ids,
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

    profile = getattr(request.user, "profile", None)

    bodyweight = ""

    if profile and profile.bodyweight:
        bodyweight = profile.bodyweight

    return render(
        request,
        'tracker/add_exercise.html',
        {
            'form': form,
            'routine': routine,
            'bodyweight': bodyweight,
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
        selected_name = request.GET.get('name')

        if selected_name:
            exercise.name = selected_name

        form = ExerciseForm(instance=exercise)
    
    profile = getattr(request.user, "profile", None)

    bodyweight = ""

    if profile and profile.bodyweight:
        bodyweight = profile.bodyweight

    return render(
        request,
        'tracker/edit_exercise.html',
        {
            'form': form,
            'routine': routine,
            'exercise': exercise,
            'bodyweight': bodyweight,
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

@login_required
def duplicate_routine(request, routine_id):
    routine = get_object_or_404(
        WorkoutRoutine,
        id=routine_id,
        user=request.user
    )

    if request.method == "POST":
        new_routine = WorkoutRoutine.objects.create(
            user=request.user,
            name=f"{routine.name} Copy",
            workout_date=routine.workout_date,
            notes=routine.notes
        )

        for exercise in routine.exercises.all():
            Exercise.objects.create(
                routine=new_routine,
                name=exercise.name,
                sets=exercise.sets,
                reps=exercise.reps,
                weight=exercise.weight
            )

        messages.success(request, "Workout routine duplicated successfully.")
        return redirect('edit_routine', routine_id=new_routine.id)

    return render(
        request,
        'tracker/duplicate_routine.html',
        {'routine': routine}
    )