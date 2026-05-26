from django.contrib import admin
from .models import Workout, WorkoutRoutine, Exercise

# Register your models here.
admin.site.register(Workout)
admin.site.register(WorkoutRoutine)
admin.site.register(Exercise)