from django.urls import path
from .templates.tracker import views

urlpatterns = [
    path('', views.home, name='home'),
]