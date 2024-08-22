from django.urls import path
from . import views

urlpatterns = [
    path('list_clips/', views.list_clips, name='list_clips'),
    path('view_clip/<int:id>/', views.view_clip, name='view_clip'),
    path('api/clips/', views.create_clip, name='create_clip'),
    path('api/clips/', views.list_clips, name='list_clips'),
    path('api/clips/<int:id>/', views.view_clip, name='view_clip'),
    path('api/clips/<int:id>/', views.update_clip, name='update_clip'),
    path('api/clips/<int:id>/', views.delete_clip, name='delete_clip'),
]