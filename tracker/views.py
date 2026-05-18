from django.shortcuts import render, redirect
from .models import Workout
from .forms import WorkoutForm

# Create your views here.
def home(request):

    workouts = Workout.objects.all().order_by('-workout_date')

    search_query = request.GET.get('search', '')

    if search_query:
        workouts = workouts.filter(
            workout_name__icontains=search_query
        )

    total_workouts = workouts.count()

    total_sets = sum(workout.sets for workout in workouts)

    total_weight = sum(
        workout.weight * workout.sets * workout.reps
        for workout in workouts
    )

    recent_workouts = workouts[:5]

    context = {
        'workouts': workouts,
        'total_workouts': total_workouts,
        'total_sets': total_sets,
        'total_weight': total_weight,
        'recent_workouts': recent_workouts,
    }

    return render(request, 'tracker/home.html', context)

def add_workout(request):
    if request.method == "POST":
        form = WorkoutForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('home')
        
    else:
        form = WorkoutForm()
    
    return render(request, 'tracker/add_workout.html', {'form': form})

def edit_workout(request, workout_id):

    workout = Workout.objects.get(id=workout_id)

    if request.method == 'POST':

        form = WorkoutForm(request.POST, instance=workout)

        if form.is_valid():
            form.save()
            return redirect('home')
    
    else:
        form = WorkoutForm(instance=workout)

    context = {
        'form': form
    }

    return render(request, 'tracker/edit_workout.html', context)

def delete_workout(request, workout_id):

    workout = Workout.objects.get(id=workout_id)

    if request.method == 'POST':
        workout.delete()
        return redirect('home')
    
    context = {
        'workout': workout
    }

    return render(request, 'tracker/delete_workout.html', context)