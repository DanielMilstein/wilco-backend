from django.urls import path
from . import views

urlpatterns = [
    path('create_report/', views.create_report, name='create_report'),
    path('create_report_objective/', views.create_report_objective, name='create_report_objective'),
    path('list_reports/', views.list_reports, name='list_reports'),
    path('view_report/<int:id>/', views.view_report, name='view_report'),

]