# urls.py
from django.urls import path
from . import views

app_name = 'task_display'

urlpatterns = [
    path('', views.task_list_view, name='task_list'),

]