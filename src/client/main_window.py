"""
Главное окно для ADITIM Monitor Client
"""

from PySide6.QtWidgets import QMainWindow, QMessageBox, QVBoxLayout
from PySide6.QtCore import QFile
from PySide6.QtUiTools import QUiLoader

from .resources import UI_PATHS
from .widgets.home_page import HomePage
from .windows.window_profiles import ProfilesContent


class MainWindow(QMainWindow):
    """Главное окно приложения с переключаемым контентом"""
    
    def __init__(self):
        super().__init__()
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
        # Создаем домашнюю страницу
        self.home_page = HomePage()
        layout = QVBoxLayout(self.home_page)
        layout.addWidget(self.home_page.ui)
        
        # Создаем содержимое профилей
        self.profiles_content = ProfilesContent()
        layout = QVBoxLayout(self.profiles_content)
        layout.addWidget(self.profiles_content.ui)
        
        # Добавляем в стек
        self.ui.stackedWidget_content.addWidget(self.home_page)
        self.ui.stackedWidget_content.addWidget(self.profiles_content)

    def setup_ui(self):
        """Настройка UI компонентов после загрузки"""
        # Подключаем меню навигации
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
        self.ui.stackedWidget_content.setCurrentWidget(self.home_page)
        self.setWindowTitle("ADITIM Monitor")

    def show_profiles(self):
        """Показать профили"""
        self.ui.stackedWidget_content.setCurrentWidget(self.profiles_content)
        self.setWindowTitle("ADITIM Monitor - Профили")

    def show_products(self):
        """Показать изделия"""
        QMessageBox.information(self, "Изделия", "Окно изделий (в разработке)")

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
