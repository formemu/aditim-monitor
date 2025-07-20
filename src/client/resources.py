"""
Единый файл ресурсов для ADITIM Monitor
"""

import os
from pathlib import Path

# Базовый путь к ресурсам
BASE_PATH = Path(__file__).parent

# Пути к UI файлам
UI_PATHS = {
    "MAIN_WINDOW": str(BASE_PATH / "ui" / "main_window.ui"),
    "HOME_PAGE": str(BASE_PATH / "ui" / "home_page.ui"),
    "PROFILES_CONTENT": str(BASE_PATH / "ui" / "window_profiles.ui"),
    "DIALOG_CREATE_PROFILE": str(BASE_PATH / "ui" / "dialog_create_profile.ui"),
}

# Пути к иконкам
ICON_PATHS = {
    "ADD": str(BASE_PATH / "resources" / "icons" / "icon_add.svg"),
    "EDIT": str(BASE_PATH / "resources" / "icons" / "icon_edit.svg"), 
    "DELETE": str(BASE_PATH / "resources" / "icons" / "icon_delete.svg"),
    "LOGO": str(BASE_PATH / "resources" / "icons" / "aditim_logo.ico"),
    "LOGO_PNG": str(BASE_PATH / "resources" / "icons" / "aditim_logo.png"),
    "LOGO_JPG": str(BASE_PATH / "resources" / "icons" / "aditim_logo2.jpg"),
}

# Пути к стилям
STYLE_PATHS = {
    "MAIN": str(BASE_PATH / "resources" / "styles" / "main_template.qss"),
    "DIALOGS": str(BASE_PATH / "resources" / "styles" / "dialogs_template.qss"),
}
