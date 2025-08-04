# ADITIM Task Viewer - Django Server

Django сервер для отображения задач из базы данных ADITIM Monitor.

## Запуск сервера

```bash
cd src/django_server
python manage.py runserver 0.0.0.0:8080
```

## Доступные страницы

- Список задач: http://localhost:8080/
- Детали задачи: http://localhost:8080/task/{id}/
- API задач: http://localhost:8080/api/task/

## Особенности

- Соблюдение золотых правил ADITIM (единственное число, тип→содержимое)
- Использование существующей базы данных ADITIM Monitor
- Фильтрация и поиск задач
- Пагинация результатов
- Bootstrap UI для адаптивного дизайна

## Структура

- `task_display/models.py` - модели Django для существующих таблиц
- `task_display/views.py` - представления для отображения задач  
- `templates/` - HTML шаблоны
- `aditim_task_viewer/settings.py` - настройки проекта
