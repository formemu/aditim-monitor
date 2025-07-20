"""
Constants for ADITIM Monitor Client
"""

import os

API_BASE_URL = os.getenv('ADITIM_API_URL', 'http://127.0.0.1:8000')
API_TIMEOUT = int(os.getenv('ADITIM_API_TIMEOUT', '30'))

# UI Colors
COLORS = {
    "COLOR_LOGO": "#14426a",
    "COLOR_PRIMARY": "#2196F3",
    "COLOR_ERROR": "#F44336",
    "COLOR_BACKGROUND": "#181B20",
}

# UI Fonts
FONTS = {
    "FONT_TEXT_HEADER": ("Arial", 24, "bold"),
    "FONT_TEXT": ("Arial", 12, "normal"),
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