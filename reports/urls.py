from django.urls import path
from . import views

urlpatterns = [
    path('create_report/', views.create_report, name='create_report'),
    path('create_report_objective/', views.create_report_objective, name='create_report_objective'),
    path('list_reports/', views.list_reports, name='list_reports'),
    path('view_report/<int:id>/', views.view_report, name='view_report'),
    path('api/reports/', views.api_create_report, name='api_create_report'),
    path('api/reports/', views.api_list_reports, name='api_list_reports'),
    path('api/reports/<int:id>/', views.api_view_report, name='api_view_report'),
    path('api/reports/<int:id>/', views.api_update_report, name='api_update_report'),
    path('api/reports/<int:id>/', views.api_delete_report, name='api_delete_report'),
    path('api/report_objectives/', views.api_create_report_objective, name='api_create_report_objective'),
    path('api/report_objectives/', views.api_list_report_objectives, name='api_list_report_objectives'),
    path('api/report_objectives/<int:id>/', views.api_view_report_objective, name='api_view_report_objective'),
    path('api/report_objectives/<int:id>/', views.api_update_report_objective, name='api_update_report_objective'),
    path('api/report_objectives/<int:id>/', views.api_delete_report_objective, name='api_delete_report_objective'),
    path('api/send_report/', views.api_send_report, name='api_send_report'),

]