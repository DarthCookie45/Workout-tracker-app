from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

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
        'accounts/login/',
        auth_views.LoginView.as_view(
            template_name='registration/login.html',
            redirect_authenticated_user=True
        ),
        name='login'
    ),

    path(
        'accounts/logout/',
        auth_views.LogoutView.as_view(),
        name='logout'
    ),

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

    path(
        'workouts/<int:routine_id>/duplicate/',
        views.duplicate_routine,
        name='duplicate_routine'
    ),

    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(
            template_name="tracker/password_reset.html",
            email_template_name="tracker/password_reset_email.html",
            subject_template_name="tracker/password_reset_subject.txt",
        ),
        name="password_reset",
    ),

    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="tracker/password_reset_done.html"
        ),
        name="password_reset_done",
    ),

    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="tracker/password_reset_confirm.html"
        ),
        name="password_reset_confirm",
    ),

    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="tracker/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
]
