from django.db import models

# Create your models here.
class Workout(models.Model):
    workout_name = models.CharField(max_length=100)
    exercise = models.CharField(max_length=100)
    sets = models.PositiveIntegerField()
    reps = models.PositiveIntegerField()
    weight = models.DecimalField(max_digits=5, decimal_places=2)
    workout_date = models.DateField()
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.workout_name} - {self.exercise}"