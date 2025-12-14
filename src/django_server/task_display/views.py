# views.py

from django.shortcuts import render
from .models import Task


def task_list_view(request):
    """Отображение списка задач (только в работе, исключая разработку)"""
    list_task = Task.objects.exclude(type_id=0).select_related(
        'product__department',
        'profiletool__profile',
        'status',
        'type'
    ).prefetch_related(
        'component_list'
    ).filter(
        status__name="В работе"
    ).exclude(
        status__name="Выполнена"
    )
    
    return render(request, 'task_display/task_list.html', {'task_list': list_task})