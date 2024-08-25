from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('', views.home, name='home'),
    path('filter_clips/', views.filter_clips, name='filter_clips'),
    path('filter_clips2/', views.filter_clips2, name='filter_clips2'),
]