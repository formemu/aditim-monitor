"""
Constants for ADITIM Monitor Client
"""

import os
from pathlib import Path

# Базовый путь к client директории
CLIENT_BASE_PATH = Path(__file__).parent

API_BASE_URL = os.getenv('ADITIM_API_URL', 'http://127.0.0.1:8000')
API_TIMEOUT = int(os.getenv('ADITIM_API_TIMEOUT', '30'))

# UI Colors - ADITIM Corporate Style
COLORS = {
    # Основные корпоративные цвета ADITIM
    "COLOR_PRIMARY": "#14426a",        # Основной синий ADITIM (логотип, акценты)
    "COLOR_PRIMARY_LIGHT": "#1a5580",  # Светлый вариант основного
    "COLOR_PRIMARY_DARK": "#262a35",   # Темный вариант основного
    "COLOR_SECONDARY": "#f8f9fa",      # Светло-серый (фон карточек)
}

# UI Fonts - Современная типографика
FONTS = {
    "FONT_FAMILY_PRIMARY": "Segoe UI, system-ui, sans-serif",
    "FONT_FAMILY_SECONDARY": "Roboto, Arial, sans-serif", 
    "FONT_SIZE_LARGE": "24px",
    "FONT_SIZE_MEDIUM": "18px",
    "FONT_SIZE_SMALL": "14px",
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
    "DIALOGS": "resources/styles/dialogs_template.qss",
    "HOME_PAGE": "resources/styles/home_page_template.qss"
}


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