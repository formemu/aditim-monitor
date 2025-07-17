"""
Constants for ADITIM Monitor Client
"""

# API Configuration
API_BASE_URL = "http://localhost:8000"
API_TIMEOUT = 30

# UI Colors
COLORS = {
    "PRIMARY": "#2196F3",
    "SECONDARY": "#FFC107", 
    "SUCCESS": "#4CAF50",
    "ERROR": "#F44336",
    "BACKGROUND": "#181B20",
    "SURFACE": "#23262B",
    "TEXT_PRIMARY": "#FFFFFF",
    "TEXT_SECONDARY": "#90CAF9"
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