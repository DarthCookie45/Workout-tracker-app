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

]