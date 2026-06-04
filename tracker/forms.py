from django import forms
from .models import Workout
from .models import WorkoutRoutine
from .models import Exercise
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


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


class WorkoutRoutineForm(forms.ModelForm):
    class Meta:
        model = WorkoutRoutine
        fields = [
            'name',
            'workout_date',
            'notes',
            'colour',
        ]

        widgets = {
            'workout_date': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control'
                }
            ),
            'colour': forms.Select(
                attrs={'class': 'form-select'}
            ),
        }


class ExerciseForm(forms.ModelForm):
    class Meta:
        model = Exercise

        fields = [
            'name',
            'sets',
            'reps',
            'weight',
        ]

        widgets = {
            'name': forms.TextInput(
                attrs={'class': 'form-control'}
            ),

            'sets': forms.NumberInput(
                attrs={'class': 'form-control'}
            ),

            'reps': forms.TextInput(
                attrs={'class': 'form-control'}
            ),

            'weight': forms.NumberInput(
                attrs={'class': 'form-control'}
            ),
        }

    def clean_name(self):
        name = self.cleaned_data.get("name")

        if name:
            return name.strip().title()

        return name


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'password1',
            'password2',
        ]
