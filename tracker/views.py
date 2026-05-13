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