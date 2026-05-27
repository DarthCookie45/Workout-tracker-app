from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    path(
        'add/',
        views.add_workout,
        name='add_workout'
    ),

    path(
        'edit/<int:workout_id>/',
        views.edit_workout,
        name='edit_workout'
    ),

    path(
        'delete/<int:workout_id>/',
        views.delete_workout,
        name='delete_workout'
    ),


    path('register/', views.register, name='register'),

    path(
    'workout/<int:workout_id>/',
    views.workout_detail,
    name='workout_detail'
    ),

    path('workouts/', views.workouts, name='workouts'),
    path('progress/', views.progress, name='progress'),
    path('calendar/', views.calendar, name='calendar'),
    path('profile/', views.profile, name='profile'),

    path('workouts/add/', views.add_routine, name='add_routine'),

    path(
    'workouts/<int:routine_id>/',
    views.routine_detail,
    name='routine_detail'
    ),

    path(
    'workouts/<int:routine_id>/add-exercise/',
    views.add_exercise,
    name='add_exercise'
    ),

    path(
    'exercise/<int:exercise_id>/edit/',
    views.edit_exercise,
    name='edit_exercise'
    ),

    path(
    'exercise/<int:exercise_id>/delete/',
    views.delete_exercise,
    name='delete_exercise'
    ),

    path(
    'workouts/<int:routine_id>/edit/',
    views.edit_routine,
    name='edit_routine'
    ),

    path(
    'workouts/<int:routine_id>/delete/',
    views.delete_routine,
    name='delete_routine'
    ),

    path(
    'workouts/<int:routine_id>/exercise-library/',
    views.exercise_library,
    name='exercise_library'
    ),
]