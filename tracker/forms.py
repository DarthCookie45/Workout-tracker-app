from django import forms
from .models import Workout

class WorkoutForm(forms.ModelForm):
    class Meta:
        model = Workout

        fields = [
            'workout_name',
            'exercise',
            'muscle_group',
            'sets',
            'reps',
            'weight',
            'workout_date',
            'notes'
        ]

        widgets = {
            'workout_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Arm Day'
            }),

            'exercise': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Dumbbell Curls'
            }),

            'sets': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. 3'
            }),
            'reps': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. 10'
            }),
            'weight': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. 50'
            }),

            'workout_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),

            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Additional notes about the workout...'
            })
        }