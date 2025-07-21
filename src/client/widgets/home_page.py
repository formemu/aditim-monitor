"""
Домашняя страница (заставка) для ADITIM Monitor Client
"""

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import QFile, Signal, Qt
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QPixmap

from ..constants import UI_PATHS_ABS as UI_PATHS, ICON_PATHS_ABS as ICON_PATHS, get_style_path
from ..style_utils import load_styles_with_constants


class HomePage(QWidget):
    """Домашняя страница с навигационными кнопками"""
    
    # Сигналы для навигации
    profiles_requested = Signal()
    products_requested = Signal()
    blanks_requested = Signal()
    tasks_requested = Signal()
    settings_requested = Signal()
    reports_requested = Signal()
    
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

    def apply_home_page_styles(self):
        """Применяет стили к главной странице"""
        style_path = get_style_path("HOME_PAGE")
        style_sheet = load_styles_with_constants(style_path)
        self.ui.setStyleSheet(style_sheet)

    def load_logo(self):
        """Загрузка и установка логотипа"""
        try:
            # Попробуем загрузить логотип
            logo_path = ICON_PATHS["LOGO_JPG"]
            pixmap = QPixmap(logo_path)
            
            if not pixmap.isNull():
                # Масштабируем логотип с сохранением пропорций (увеличиваем размер на 20%)
                scaled_pixmap = pixmap.scaled(
                    480, 192,  # увеличенные размеры на 20%
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                self.ui.label_logo.setPixmap(scaled_pixmap)
                self.ui.label_logo.setText("")  # Убираем текст-заглушку
            else:
                # Если логотип не загрузился, оставляем текст
                self.ui.label_logo.setText("ADITIM Monitor")
                
        except Exception as e:
            print(f"Ошибка загрузки логотипа: {e}")
            self.ui.label_logo.setText("ADITIM Monitor")
