"""Главное окно для ADITIM Monitor Client"""
from PySide6.QtWidgets import QMainWindow, QMessageBox
from PySide6.QtCore import QFile
from PySide6.QtUiTools import QUiLoader

from .constant import UI_PATHS_ABS as UI_PATHS, STYLE_PATHS_ABS as STYLE_PATHS
from .style_util import load_styles
from .widgets.home_page import HomePage
from .windows.window_profile import WindowProfile
from .windows.window_development import WindowDevelopment
from .windows.window_product import WindowProduct
from .windows.window_task import WindowTask
from .windows.window_machine import WindowMachine
from .windows.window_blank import WindowBlank
from .windows.window_setting import WindowSetting



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
        """Настройка stacked widget: только домашняя страница создаётся сразу"""
        # Очищаем stackedWidget
        while self.ui.stackedWidget_content.count() > 0:
            widget = self.ui.stackedWidget_content.widget(0)
            self.ui.stackedWidget_content.removeWidget(widget)
            widget.deleteLater()
        # Создаём домашнюю страницу
        self.home_page = HomePage()
        self.ui.stackedWidget_content.addWidget(self.home_page.ui)
        self.ui.stackedWidget_content.setCurrentWidget(self.home_page.ui)
        # Ленивая инициализация: окна создаются при первом вызове
        self.window_profile = None
        self.window_development = None
        self.window_product = None
        self.window_task = None
        self.window_machine = None
        self.window_blank = None
        self.window_setting = None

    def setup_ui(self):
        """Настройка UI компонентов после загрузки"""
        # Загружаем и применяем стили
        style_sheet = load_styles(STYLE_PATHS["MAIN"])
        self.setStyleSheet(style_sheet)

        # Подключаем действия меню навигации
        self.ui.action_home.triggered.connect(self.show_home)
        self.ui.action_profile.triggered.connect(self.show_profile)
        self.ui.action_development.triggered.connect(self.show_development)
        self.ui.action_product.triggered.connect(self.show_product)
        self.ui.action_blank.triggered.connect(self.show_blank)
        self.ui.action_task.triggered.connect(self.show_task)
        self.ui.action_setting.triggered.connect(self.show_setting)
        self.ui.action_report.triggered.connect(self.show_report)
        self.ui.action_machine.triggered.connect(self.show_machine)

        # Подключаем сигналы домашней страницы
        self.home_page.profile_requested.connect(self.show_profile)
        self.home_page.product_requested.connect(self.show_product)
        self.home_page.development_requested.connect(self.show_development)
        self.home_page.blank_requested.connect(self.show_blank)
        self.home_page.task_requested.connect(self.show_task)
        self.home_page.setting_requested.connect(self.show_setting)
        self.home_page.report_requested.connect(self.show_report)
        self.home_page.machine_requested.connect(self.show_machine)

    def ensure_window_created(self, attr_name, window_class):
        """Создаёт окно, если ещё не создано, и добавляет в стек"""
        window = getattr(self, attr_name)
        if window is None:
            window = window_class()
            setattr(self, attr_name, window)
            self.ui.stackedWidget_content.addWidget(window.ui)
        return window


    def show_home(self):
        """Показать домашнюю страницу"""
        self.ui.stackedWidget_content.setCurrentWidget(self.home_page.ui)
        self.setWindowTitle("ADITIM Monitor")


    def show_profile(self):
        """Показать профили"""
        window = self.ensure_window_created("window_profile", WindowProfile)
        self.ui.stackedWidget_content.setCurrentWidget(window.ui)
        self.setWindowTitle("ADITIM Monitor - Профили")

    def show_development(self):
        """Показать разработки"""
        window = self.ensure_window_created("window_development", WindowDevelopment)
        self.ui.stackedWidget_content.setCurrentWidget(window.ui)
        self.setWindowTitle("ADITIM Monitor - Разработки")

    def show_product(self):
        """Показать изделия"""
        window = self.ensure_window_created("window_product", WindowProduct)
        self.ui.stackedWidget_content.setCurrentWidget(window.ui)
        self.setWindowTitle("ADITIM Monitor - Изделия")

    def show_task(self):
        """Показать задачи"""
        window = self.ensure_window_created("window_task", WindowTask)
        self.ui.stackedWidget_content.setCurrentWidget(window.ui)
        self.setWindowTitle("ADITIM Monitor - Задачи")

    def show_machine(self):
        """Показать станки"""
        window = self.ensure_window_created("window_machine", WindowMachine)
        self.ui.stackedWidget_content.setCurrentWidget(window.ui)
        self.setWindowTitle("ADITIM Monitor - Станки")

    def show_blank(self):
        """Показать заготовки"""
        window = self.ensure_window_created("window_blank", WindowBlank)
        self.ui.stackedWidget_content.setCurrentWidget(window.ui)
        self.setWindowTitle("ADITIM Monitor - Заготовки")

    def show_setting(self):
        """Показать настройки"""
        window = self.ensure_window_created("window_setting", WindowSetting)
        self.ui.stackedWidget_content.setCurrentWidget(window.ui)
        self.setWindowTitle("ADITIM Monitor - Настройки")

    def show_report(self):
        """Показать отчеты"""
        QMessageBox.information(self, "Отчеты", "Отчеты (в разработке)")