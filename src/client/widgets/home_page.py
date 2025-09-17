"""
Домашняя страница (заставка) для ADITIM Monitor Client
"""

import os
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import QFile, Signal, Qt
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QPixmap

from ..constant import UI_PATHS_ABS as UI_PATHS, ICON_PATHS_ABS as ICON_PATHS, get_style_path
from ..style_util import load_styles


class HomePage(QWidget):
    """Домашняя страница с навигационными кнопками"""
    
    # Сигналы для навигации
    profiles_requested = Signal()
    products_requested = Signal()
    blanks_requested = Signal()
    tasks_requested = Signal()
    settings_requested = Signal()
    reports_requested = Signal()
    machines_requested = Signal()

    def __init__(self):
        super().__init__()
        self.load_ui()
        self.setup_ui()

    def load_ui(self):
        """Загрузка UI из файла"""
        ui_file = QFile(UI_PATHS["HOME_PAGE"])
        ui_file.open(QFile.ReadOnly)
        
        loader = QUiLoader()
        self.ui = loader.load(ui_file)
        ui_file.close()

    def setup_ui(self):
        """Настройка UI компонентов после загрузки"""
        # Загрузка и установка логотипа
        self.load_logo()
        
        # Применяем стили главной страницы
        self.apply_home_page_styles()
        
        # Подключение кнопок
        self.ui.pushButton_profiles_open.clicked.connect(self.profiles_requested.emit)
        self.ui.pushButton_products_open.clicked.connect(self.products_requested.emit)
        self.ui.pushButton_blanks_open.clicked.connect(self.blanks_requested.emit)
        self.ui.pushButton_tasks_open.clicked.connect(self.tasks_requested.emit)
        self.ui.pushButton_settings_open.clicked.connect(self.settings_requested.emit)
        self.ui.pushButton_reports_open.clicked.connect(self.reports_requested.emit)
        self.ui.pushButton_machines_open.clicked.connect(self.machines_requested.emit)

    def apply_home_page_styles(self):
        """Применяет стили к главной странице"""
        style_path = get_style_path("HOME_PAGE")
        style_sheet = load_styles(style_path)
        self.ui.setStyleSheet(style_sheet)

    def load_logo(self):
        """Загрузка и установка логотипа"""
        try:
            # Сначала пробуем PNG, затем JPG
            for logo_key in ["LOGO_PNG", "LOGO_JPG"]:
                logo_path = ICON_PATHS[logo_key]
                
                # Проверяем существование файла
                if not os.path.exists(logo_path):
                    continue
                    
                pixmap = QPixmap(logo_path)
                
                if not pixmap.isNull() and pixmap.width() > 0 and pixmap.height() > 0:
                    # Ограничиваем максимальные размеры для предотвращения ошибок памяти
                    max_width, max_height = 400, 160
                    
                    # Масштабируем логотип с сохранением пропорций
                    scaled_pixmap = pixmap.scaled(
                        max_width, max_height,
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation
                    )
                    
                    # Проверяем корректность масштабированного изображения
                    if not scaled_pixmap.isNull():
                        self.ui.label_logo.setPixmap(scaled_pixmap)
                        self.ui.label_logo.setText("")  # Убираем текст-заглушку
                        return  # Успешно загрузили
            
            # Если ни один логотип не загрузился, оставляем текст
            self.ui.label_logo.setText("ADITIM Monitor")
                
        except Exception as e:
            print(f"Ошибка загрузки логотипа: {e}")
            self.ui.label_logo.setText("ADITIM Monitor")
