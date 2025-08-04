from django.urls import path
from . import views

app_name = 'task_display'

urlpatterns = [
    path('', views.task_list_view, name='task_list'),
    path('task/<int:task_id>/', views.task_detail_view, name='task_detail'),
    path('api/task/', views.task_api_view, name='task_api'),
]
