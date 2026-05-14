from django.shortcuts import render, redirect
from .models import Workout
from .forms import WorkoutForm

# Create your views here.
def home(request):

    workouts = Workout.objects.all()

    if request.method == 'POST':

        form = WorkoutForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('home')
    
    else:
        form = WorkoutForm()
    
    context = {
        'workouts': workouts,
        'form': form
    }
    
    return render(request, 'tracker/home.html', context)

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