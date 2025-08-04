from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from .models import Task, DirTaskStatus, DirDepartment
from datetime import datetime

def task_list_view(request):
    """Отображение списка задач"""
    # Получение параметров фильтрации
    status_filter = request.GET.get('status')
    department_filter = request.GET.get('department')
    search_query = request.GET.get('search')
    
    # Базовый запрос
    task_queryset = Task.objects.select_related(
        'product', 'profile_tool__profile', 'department', 'status'
    ).prefetch_related('component_list')
    
    # Применение фильтров
    if status_filter:
        task_queryset = task_queryset.filter(status_id=status_filter)
    
    if department_filter:
        task_queryset = task_queryset.filter(department_id=department_filter)
    
    if search_query:
        task_queryset = task_queryset.filter(
            Q(product__name__icontains=search_query) |
            Q(profile_tool__profile__article__icontains=search_query)
        )
    
    # Пагинация
    paginator = Paginator(task_queryset, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Данные для фильтров
    status_list = DirTaskStatus.objects.all()
    department_list = DirDepartment.objects.all()
    
    context = {
        'page_obj': page_obj,
        'status_list': status_list,
        'department_list': department_list,
        'current_status': status_filter,
        'current_department': department_filter,
        'search_query': search_query,
    }
    
    return render(request, 'task_display/task_list.html', context)

def task_detail_view(request, task_id):
    """Детальное отображение задачи"""
    task = get_object_or_404(
        Task.objects.select_related(
            'product', 'profile_tool__profile', 'department', 'status'
        ).prefetch_related('component_list'),
        id=task_id
    )
    
    context = {
        'task': task,
    }
    
    return render(request, 'task_display/task_detail.html', context)

def task_api_view(request):
    """API endpoint для получения данных задач"""
    task_list = Task.objects.select_related(
        'product', 'profile_tool__profile', 'department', 'status'
    ).all()
    
    data = []
    for task in task_list:
        data.append({
            'id': task.id,
            'name': task.get_display_name(),
            'status': task.status.name,
            'department': task.department.name,
            'position': task.position,
            'deadline_on': task.deadline_on.isoformat() if task.deadline_on else None,
            'created_at': task.created_at.isoformat(),
        })
    
    return JsonResponse({
        'task_list': data,
        'timestamp': datetime.now().isoformat(),
        'count': len(data)
    })

def task_live_update_api(request):
    """API для получения обновлений в реальном времени"""
    # Получение параметров фильтрации
    status_filter = request.GET.get('status')
    department_filter = request.GET.get('department')
    search_query = request.GET.get('search')
    page = int(request.GET.get('page', 1))
    
    # Базовый запрос
    task_queryset = Task.objects.select_related(
        'product', 'profile_tool__profile', 'department', 'status'
    ).prefetch_related('component_list')
    
    # Применение фильтров
    if status_filter:
        task_queryset = task_queryset.filter(status_id=status_filter)
    
    if department_filter:
        task_queryset = task_queryset.filter(department_id=department_filter)
    
    if search_query:
        task_queryset = task_queryset.filter(
            Q(product__name__icontains=search_query) |
            Q(profile_tool__profile__article__icontains=search_query)
        )
    
    # Пагинация
    paginator = Paginator(task_queryset, 20)
    page_obj = paginator.get_page(page)
    
    # Формирование данных
    tasks_data = []
    for task in page_obj:
        tasks_data.append({
            'id': task.id,
            'name': task.get_display_name(),
            'status': task.status.name,
            'department': task.department.name,
            'position': task.position,
            'deadline_on': task.deadline_on.strftime('%d.%m.%Y') if task.deadline_on else None,
            'created_at': task.created_at.strftime('%d.%m.%Y %H:%M'),
            'url': f'/task/{task.id}/',
        })
    
    return JsonResponse({
        'tasks': tasks_data,
        'has_previous': page_obj.has_previous(),
        'has_next': page_obj.has_next(),
        'current_page': page_obj.number,
        'total_pages': page_obj.paginator.num_pages,
        'total_count': page_obj.paginator.count,
        'timestamp': datetime.now().isoformat(),
    })
