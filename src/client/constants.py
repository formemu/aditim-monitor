"""
Constants for ADITIM Monitor Client
"""

import os

# API Configuration (поддержка VPN и внешнего подключения через переменные окружения)
# Задайте переменную окружения ADITIM_API_URL, например: http://<host-ip>:8000
API_BASE_URL = os.getenv('ADITIM_API_URL', 'http://127.0.0.1:8000') # Заменено localhost на 127.0.0.1 для совместимости с VPN
API_TIMEOUT = int(os.getenv('ADITIM_API_TIMEOUT', '30'))

# UI Colors
COLORS = {
    "COLOR_PRIMARY": "#2196F3",
    "COLOR_SECONDARY": "#2196F3", 
    "COLOR_SUCCESS": "#2196F3",
    "COLOR_ERROR": "#F44336",
    "COLOR_BACKGROUND": "#181B20",
    "COLOR_SURFACE": "#23262B",
    "COLOR_TEXT_PRIMARY": "#FFFFFF",
    "COLOR_TEXT_SECONDARY": "#90CAF9"
}

# UI Fonts
FONTS = {
    "HEADER": ("Arial", 16, "bold"),
    "BODY": ("Arial", 12, "normal"),
    "SMALL": ("Arial", 10, "normal")
}

# UI Sizes
SIZES = {
    "MAIN_WINDOW_WIDTH": 1200,
    "MAIN_WINDOW_HEIGHT": 800,
    "BUTTON_HEIGHT": 32,
    "ICON_SIZE": 24,
    "MARGIN": 10
}

# File Paths
PATHS = {
    "MAIN_STYLE": "src/client/resources/styles/main.qss",
    "DIALOG_STYLE": "src/client/resources/styles/dialogs.qss", 
    "ICONS": "src/client/resources/icons/",
    "IMAGES": "src/client/resources/images/"
}

# Task Statuses
TASK_STATUSES = [
    {"id": 1, "name": "Новая"},
    {"id": 2, "name": "В работе"},
    {"id": 3, "name": "Выполнена"},
    {"id": 4, "name": "Отменена"}
]

# Update intervals
UPDATE_INTERVAL_MS = 5000  # 5 seconds
MAX_ACTIVE_TASKS = 10

# Profile Equipment Types (7 standard types)
PROFILE_EQUIPMENT = [
    "плиты 1",
    "плиты 2", 
    "плиты 3",
    "плиты 4",
    "пальцы",
    "усреднитель",
    "кондуктор"
]

# Work Types
WORK_TYPES = [
    "новый инструмент",
    "новый вариант", 
    "добавить к существующему",
    "переделать",
    "доработка"
]