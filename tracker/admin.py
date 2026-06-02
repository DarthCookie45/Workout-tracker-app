from django.contrib import admin
from .models import Workout, WorkoutRoutine, Exercise, WorkoutSchedule

# Register your models here.
admin.site.register(Workout)
admin.site.register(WorkoutRoutine)
admin.site.register(Exercise)
admin.site.register(WorkoutSchedule)
from .models import Profile
admin.site.register(Profile)