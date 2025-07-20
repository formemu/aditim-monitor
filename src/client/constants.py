"""
Constants for ADITIM Monitor Client
"""

import os
from pathlib import Path

# Базовый путь к client директории
CLIENT_BASE_PATH = Path(__file__).parent

API_BASE_URL = os.getenv('ADITIM_API_URL', 'http://127.0.0.1:8000')
API_TIMEOUT = int(os.getenv('ADITIM_API_TIMEOUT', '30'))

# UI Colors
COLORS = {
    "COLOR_LOGO": "#14426a",
    "COLOR_PRIMARY": "#2196F3",
    "COLOR_SECONDARY": "#FFC107",
    "COLOR_SUCCESS": "#4CAF50",
    "COLOR_ERROR": "#F44336",
    "COLOR_WARNING": "#FF9800",
    "COLOR_INFO": "#2196F3",
    "COLOR_BACKGROUND": "#f5f5f5",
    "COLOR_BACKGROUND_MAIN": "#262a35",
    "COLOR_MENU_BUTTON": "#14426a",
    "COLOR_TEXT_PRIMARY": "#333333",
    "COLOR_TEXT_SECONDARY": "#666666",
    "COLOR_BORDER": "#666666",
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

# UI Paths (относительные пути от client директории)
UI_PATHS = {
    "MAIN_WINDOW": "ui/main_window.ui",
    "HOME_PAGE": "ui/home_page.ui", 
    "PROFILES_CONTENT": "ui/window_profiles.ui",
    "DIALOG_CREATE_PROFILE": "ui/dialog_create_profile.ui",
    "DIALOG_TASK": "ui/dialogtask.ui"
}

# Icon Paths (относительные пути от client директории)
ICON_PATHS = {
    "ADD": "resources/icons/icon_add.svg",
    "EDIT": "resources/icons/icon_edit.svg",
    "DELETE": "resources/icons/icon_delete.svg", 
    "LOGO": "resources/icons/aditim_logo.ico",
    "LOGO_PNG": "resources/icons/aditim_logo.png",
    "LOGO_JPG": "resources/icons/aditim_logo2.jpg"
}

# Style Paths (относительные пути от client директории)
STYLE_PATHS = {
    "MAIN": "resources/styles/main_template.qss",
    "DIALOGS": "resources/styles/dialogs_template.qss"
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

# Utility functions for path resolution
def get_ui_path(ui_name: str) -> str:
    """Получить абсолютный путь к UI файлу"""
    return str(CLIENT_BASE_PATH / UI_PATHS[ui_name])

def get_icon_path(icon_name: str) -> str:
    """Получить абсолютный путь к иконке"""
    return str(CLIENT_BASE_PATH / ICON_PATHS[icon_name])

def get_style_path(style_name: str) -> str:
    """Получить абсолютный путь к файлу стилей"""
    return str(CLIENT_BASE_PATH / STYLE_PATHS[style_name])

# Создаем словари с абсолютными путями для обратной совместимости
UI_PATHS_ABS = {key: get_ui_path(key) for key in UI_PATHS.keys()}
ICON_PATHS_ABS = {key: get_icon_path(key) for key in ICON_PATHS.keys()}  
STYLE_PATHS_ABS = {key: get_style_path(key) for key in STYLE_PATHS.keys()}