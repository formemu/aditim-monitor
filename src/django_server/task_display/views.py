from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.db.models import Q
from .models import Task
from datetime import datetime

def task_list_view(request):
    """Отображение списка задач со статусом 'В работе'"""
    task_list = Task.objects.select_related(
        'product__department',
        'profile_tool__profile',
        'status'
    ).prefetch_related('component_list').filter(
        status__name="В работе"
    )

    context = {
        'task_list': task_list,
    }
    return render(request, 'task_display/task_list.html', context)


def task_detail_view(request, task_id):
    """Детальное отображение задачи"""
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


def task_api_view(request):
    """API endpoint для получения всех задач (без фильтрации)"""
    task_list = Task.objects.select_related(
        'product', 'profile_tool__profile', 'status'
    ).filter(status__name="В работе")

    data = []
    for task in task_list:
        data.append({
            'id': task.id,
            'name': task.get_display_name(),
            'status': task.status.name,
            'position': task.position,
            'deadline': task.deadline.isoformat() if task.deadline else None,
            'created': task.created.isoformat(),
        })

    return JsonResponse({
        'task_list': data,
        'timestamp': datetime.now().isoformat(),
        'count': len(data)
    })


def task_live_update_api(request):
    """API для получения всех задач (упрощённая версия без пагинации и фильтров)"""
    task_list = Task.objects.select_related(
        'product', 'profile_tool__profile', 'status'
    ).prefetch_related('component_list').filter(
        status__name="В работе"
    )

    tasks_data = []
    for task in task_list:
        tasks_data.append({
            'id': task.id,
            'name': task.get_display_name(),
            'status': task.status.name,
            'position': task.position,
            'department': task.product.department.name if task.product else '—',
            'deadline': task.deadline.strftime('%d.%m.%Y') if task.deadline else None,
            'created': task.created.strftime('%d.%m.%Y %H:%M'),
            'url': f'/task/{task.id}/',
        })

    return JsonResponse({
        'tasks': tasks_data,
        'total_count': len(tasks_data),
        'timestamp': datetime.now().isoformat(),
    })