from django.urls import path
from . import views

urlpatterns = [
    path('create_report/', views.create_report, name='create_report'),
    path('create_report_objective/', views.create_report_objective, name='create_report_objective'),
    path('list_reports/', views.list_reports, name='list_reports'),
    path('view_report/<int:id>/', views.view_report, name='view_report'),
    path('api/reports/', views.create_report, name='create_report'),
    path('api/reports/', views.list_reports, name='list_reports'),
    path('api/reports/<int:id>/', views.view_report, name='view_report'),
    path('api/reports/<int:id>/', views.update_report, name='update_report'),
    path('api/reports/<int:id>/', views.delete_report, name='delete_report'),
    path('api/report_objectives/', views.create_report_objective, name='create_report_objective'),
    path('api/report_objectives/', views.list_report_objectives, name='list_report_objectives'),
    path('api/report_objectives/<int:id>/', views.view_report_objective, name='view_report_objective'),
    path('api/report_objectives/<int:id>/', views.update_report_objective, name='update_report_objective'),
    path('api/report_objectives/<int:id>/', views.delete_report_objective, name='delete_report_objective'),

]