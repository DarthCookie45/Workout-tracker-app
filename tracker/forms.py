from django import forms
from .models import Workout

class WorkoutForm(forms.ModelForm):
    class Meta:
        model = Workout

        fields = [
            'workout_name',
            'exercise',
            'sets',
            'reps',
            'weight',
            'workout_date',
            'notes'
        ]