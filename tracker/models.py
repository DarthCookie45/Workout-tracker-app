from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator

# Create your models here.

MUSCLE_GROUP_CHOICES = [
    ('Arms', 'Arms'),
    ('Chest', 'Chest'),
    ('Back', 'Back'),
    ('Legs', 'Legs'),
    ('Shoulders', 'Shoulders'),
    ('Core', 'Core'),
]

class Workout(models.Model):

    user = models.ForeignKey(
    User,
    on_delete=models.CASCADE,
    null=True,
    blank=True
)
    
    workout_name = models.CharField(max_length=100)
    exercise = models.CharField(max_length=100)

    muscle_group = models.CharField(
    max_length=20,
    choices=MUSCLE_GROUP_CHOICES,
    default='Arms'
)
    
    sets = models.PositiveIntegerField()
    reps = models.PositiveIntegerField()
    weight = models.DecimalField(
        max_digits=6, 
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    workout_date = models.DateField()
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.workout_name} - {self.exercise}"
    
class WorkoutRoutine(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    workout_date = models.DateField()
    notes = models.TextField(blank=True)

class Exercise(models.Model):
    routine = models.ForeignKey(
        WorkoutRoutine,
        on_delete=models.CASCADE,
        related_name='exercises'
    )
    name = models.CharField(max_length=100)
    sets = models.PositiveIntegerField()
    reps = models.CharField(max_length=20)
    weight = models.DecimalField(max_digits=6, decimal_places=2)