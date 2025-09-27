# views.py

from django.shortcuts import render
from .models import Task


def task_list_view(request):
    tasks = Task.objects.select_related(
        'product__department',
        'profiletool__profile',
        'status',
        'type',
        'location'
    ).prefetch_related('component_list').filter( status__name="В работе").exclude(status__name="Выполнена")
    return render(request, 'task_display/task_list.html', {'task_list': tasks})
