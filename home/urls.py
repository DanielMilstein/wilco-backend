from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('', views.home, name='home'),
    path('', views.map_view, name='map_view'),  # Default route
    path('get_address/', views.get_address, name='get_address'),
]

