# views.py
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Task
from datetime import datetime

def task_list_view(request):
    tasks = Task.objects.select_related(
        'product__department',
        'profile_tool__profile',
        'status',
        'type'
    ).prefetch_related('component_list').filter(
        status__name="В работе"
    )
    return render(request, 'task_display/task_list.html', {'task_list': tasks})


def task_detail_view(request, task_id):
    """Детали задачи — оставляем как есть"""
    task = get_object_or_404(
        Task.objects.select_related(
            'product', 'profile_tool__profile', 'status'
        ).prefetch_related('component_list'),
        id=task_id
    )
    context = {
        'task': task,
    }
    return render(request, 'task_display/task_detail.html', context)