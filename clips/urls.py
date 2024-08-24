from django.urls import path
from . import views

urlpatterns = [
    path('list_clips/', views.list_clips, name='list_clips'),
    path('view_clip/<int:id>/', views.view_clip, name='view_clip'),
    path('api/clips/', views.api_list_clips, name='api_list_clips'),
    path('api/clips/', views.api_create_clip, name='api_create_clip'),
    path('api/clips/<int:id>/', views.api_view_clip, name='api_view_clip'),
    path('api/clips/<int:id>/', views.api_update_clip, name='api_update_clip'),
    path('api/clips/<int:id>/', views.api_delete_clip, name='api_delete_clip'),
]