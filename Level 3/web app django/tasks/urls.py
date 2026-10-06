from django.urls import path
from . import views

app_name = 'tasks'

urlpatterns = [
    path('', views.landing_view, name='landing'),
    path('dashboard/', views.dashboard_view, name='dashboard'),

    # Projects
    path('projects/', views.project_list_view, name='project_list'),
    path('projects/new/', views.project_create_view, name='project_create'),
    path('projects/<slug:slug>/', views.project_detail_view, name='project_detail'),
    path('projects/<slug:slug>/edit/', views.project_update_view, name='project_update'),
    path('projects/<slug:slug>/delete/', views.project_delete_view, name='project_delete'),

    # Tasks
    path('tasks/new/', views.task_create_view, name='task_create'),
    path('tasks/<int:pk>/', views.task_detail_view, name='task_detail'),
    path('tasks/<int:pk>/edit/', views.task_update_view, name='task_update'),
    path('tasks/<int:pk>/delete/', views.task_delete_view, name='task_delete'),
    path('tasks/<int:pk>/status/', views.task_quick_status_view, name='task_status'),

    # Audit & Activity
    path('activity/', views.activity_log_view, name='activity_log'),
]
