"""
Главное окно для ADITIM Monitor Client
"""

from PySide6.QtWidgets import QMainWindow, QMessageBox, QVBoxLayout
from PySide6.QtCore import QFile
from PySide6.QtUiTools import QUiLoader

from .constants import UI_PATHS_ABS as UI_PATHS, STYLE_PATHS_ABS as STYLE_PATHS
from .style_utils import load_styles_with_constants
from .widgets.home_page import HomePage
from .windows.window_profiles import ProfilesContent
from .windows.window_products import ProductsContent
from .api_client import ApiClient


class MainWindow(QMainWindow):
    """Главное окно приложения с переключаемым контентом"""
    
    def __init__(self):
        super().__init__()
        # Создаем API клиент
        self.api_client = ApiClient()
        self.load_ui()
        self.setup_content()
        self.setup_ui()

    def load_ui(self):
        """Загрузка UI из файла"""
        ui_file = QFile(UI_PATHS["MAIN_WINDOW"])
        ui_file.open(QFile.ReadOnly)
        
        loader = QUiLoader()
        self.ui = loader.load(ui_file)
        ui_file.close()

        self.setWindowTitle(self.ui.windowTitle())
        self.setGeometry(self.ui.geometry())
        self.setMenuBar(self.ui.menubar)
        self.setStatusBar(self.ui.statusbar)
        self.setCentralWidget(self.ui.centralwidget)

    def setup_content(self):
        """Создание виджетов содержимого"""
        # Очищаем stackedWidget от placeholder-ов
        while self.ui.stackedWidget_content.count() > 0:
            widget = self.ui.stackedWidget_content.widget(0)
            self.ui.stackedWidget_content.removeWidget(widget)
            widget.deleteLater()
        
        # Создаем домашнюю страницу
        self.home_page = HomePage()
        
        # Создаем страницу профилей с API клиентом
        self.profiles_content = ProfilesContent(self.api_client)
        
        # Создаем страницу изделий с API клиентом
        self.products_content = ProductsContent(self.api_client)
        
        # Добавляем в стек
        self.ui.stackedWidget_content.addWidget(self.home_page.ui)
        self.ui.stackedWidget_content.addWidget(self.profiles_content.ui)
        self.ui.stackedWidget_content.addWidget(self.products_content.ui)
        
        # Устанавливаем домашнюю страницу активной
        self.ui.stackedWidget_content.setCurrentWidget(self.home_page.ui)

    def setup_ui(self):
        """Настройка UI компонентов после загрузки"""
        # Загружаем и применяем стили
        style_sheet = load_styles_with_constants(STYLE_PATHS["MAIN"])
        self.setStyleSheet(style_sheet)
        
        # Подключаем действия меню навигации
        self.ui.action_home.triggered.connect(self.show_home)
        self.ui.action_profiles.triggered.connect(self.show_profiles)
        self.ui.action_products.triggered.connect(self.show_products)
        self.ui.action_blanks.triggered.connect(self.show_blanks)
        self.ui.action_tasks.triggered.connect(self.show_tasks)
        self.ui.action_settings.triggered.connect(self.show_settings)
        self.ui.action_reports.triggered.connect(self.show_reports)
        
        # Подключаем сигналы домашней страницы
        self.home_page.profiles_requested.connect(self.show_profiles)
        self.home_page.products_requested.connect(self.show_products)
        self.home_page.blanks_requested.connect(self.show_blanks)
        self.home_page.tasks_requested.connect(self.show_tasks)
        self.home_page.settings_requested.connect(self.show_settings)
        self.home_page.reports_requested.connect(self.show_reports)

    def show_home(self):
        """Показать домашнюю страницу"""
        self.ui.stackedWidget_content.setCurrentWidget(self.home_page.ui)
        self.setWindowTitle("ADITIM Monitor")

    def show_profiles(self):
        """Показать профили"""
        self.ui.stackedWidget_content.setCurrentWidget(self.profiles_content.ui)
        self.setWindowTitle("ADITIM Monitor - Профили")

    def show_products(self):
        """Показать изделия"""
        self.ui.stackedWidget_content.setCurrentWidget(self.products_content.ui)
        self.setWindowTitle("ADITIM Monitor - Изделия")

    def show_blanks(self):
        """Показать заготовки"""
        QMessageBox.information(self, "Заготовки", "Окно заготовок (в разработке)")

    def show_tasks(self):
        """Показать задачи"""
        QMessageBox.information(self, "Задачи", "Окно задач (в разработке)")

    def show_settings(self):
        """Показать настройки"""
        QMessageBox.information(self, "Настройки", "Настройки (в разработке)")

    def show_reports(self):
        """Показать отчеты"""
        QMessageBox.information(self, "Отчеты", "Отчеты (в разработке)")
