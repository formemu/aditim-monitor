"""
Единый файл ресурсов для ADITIM Monitor
"""

import os
from pathlib import Path

# Базовый путь к ресурсам
BASE_PATH = Path(__file__).parent

# Пути к UI файлам
UI_PATHS = {
}

# Пути к иконкам
ICON_PATHS = {
    "ADD": str(BASE_PATH / "resources" / "icons" / "icon_add.svg"),
    "EDIT": str(BASE_PATH / "resources" / "icons" / "icon_edit.svg"), 
    "DELETE": str(BASE_PATH / "resources" / "icons" / "icon_delete.svg"),
    "LOGO": str(BASE_PATH / "resources" / "icons" / "aditim_logo.ico"),
}

# Пути к стилям
STYLE_PATHS = {
    "MAIN": str(BASE_PATH / "resources" / "styles" / "main_template.qss"),
    "DIALOGS": str(BASE_PATH / "resources" / "styles" / "dialogs_template.qss"),
}
