"""
Домашняя страница (заставка) для ADITIM Monitor Client
"""

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import QFile, Signal
from PySide6.QtUiTools import QUiLoader

from ..resources import UI_PATHS


class HomePage(QWidget):
    """Домашняя страница с навигационными кнопками"""
    
    # Сигналы для навигации
    profiles_requested = Signal()
    products_requested = Signal()
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
        self.ui.pushButton_profiles_open.clicked.connect(self.profiles_requested.emit)
        self.ui.pushButton_products_open.clicked.connect(self.products_requested.emit)
        self.ui.pushButton_tasks_open.clicked.connect(self.tasks_requested.emit)
        self.ui.pushButton_settings_open.clicked.connect(self.settings_requested.emit)
        self.ui.pushButton_reports_open.clicked.connect(self.reports_requested.emit)
