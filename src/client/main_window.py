"""Главное окно для ADITIM Monitor Client"""
from PySide6.QtWidgets import QMainWindow, QMessageBox
from PySide6.QtCore import QFile
from PySide6.QtUiTools import QUiLoader

from .constant import UI_PATHS_ABS as UI_PATHS, STYLE_PATHS_ABS as STYLE_PATHS
from .style_util import load_styles
from .widgets.home_page import HomePage
from .windows.window_profile import WindowProfile
from .windows.window_product import WindowProduct
from .windows.window_task import WindowTask
from .windows.window_machine import WindowMachine


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
        self.window_product = None
        self.window_task = None
        self.window_machine = None

    def setup_ui(self):
        """Настройка UI компонентов после загрузки"""
        # Загружаем и применяем стили
        style_sheet = load_styles(STYLE_PATHS["MAIN"])
        self.setStyleSheet(style_sheet)

        # Подключаем действия меню навигации
        self.ui.action_home.triggered.connect(self.show_home)
        self.ui.action_profiles.triggered.connect(self.show_profiles)
        self.ui.action_products.triggered.connect(self.show_products)
        self.ui.action_blanks.triggered.connect(self.show_blanks)
        self.ui.action_tasks.triggered.connect(self.show_tasks)
        self.ui.action_settings.triggered.connect(self.show_settings)
        self.ui.action_reports.triggered.connect(self.show_reports)
        self.ui.action_machines.triggered.connect(self.show_machines)

        # Подключаем сигналы домашней страницы
        self.home_page.profiles_requested.connect(self.show_profiles)
        self.home_page.products_requested.connect(self.show_products)
        self.home_page.blanks_requested.connect(self.show_blanks)
        self.home_page.tasks_requested.connect(self.show_tasks)
        self.home_page.settings_requested.connect(self.show_settings)
        self.home_page.reports_requested.connect(self.show_reports)
        self.home_page.machines_requested.connect(self.show_machines)

    def _ensure_window_created(self, attr_name, window_class):
        """Создаёт окно, если ещё не создано, и добавляет в стек"""
        window = getattr(self, attr_name)
        if window is None:
            window = window_class()
            setattr(self, attr_name, window)
            self.ui.stackedWidget_content.addWidget(window.ui)
        return window

    def _stop_all_timers(self, except_this=None):
        """Останавливает автообновление всех окон, кроме указанного"""
        windows = [
            ("profile", self.window_profile),
            ("product", self.window_product),
            ("task", self.window_task),
            ("machine", self.window_machine),
        ]
        for name, window in windows:
            if window and name != except_this:
                window.stop_auto_refresh()

    def show_home(self):
        """Показать домашнюю страницу"""
        self._stop_all_timers()
        self.ui.stackedWidget_content.setCurrentWidget(self.home_page.ui)
        self.setWindowTitle("ADITIM Monitor")

    def show_profiles(self):
        """Показать профили"""
        self._stop_all_timers(except_this="profile")
        window = self._ensure_window_created("window_profile", WindowProfile)
        self.ui.stackedWidget_content.setCurrentWidget(window.ui)
        self.setWindowTitle("ADITIM Monitor - Профили")
        window.start_auto_refresh()

    def show_products(self):
        """Показать изделия"""
        self._stop_all_timers(except_this="product")
        window = self._ensure_window_created("window_product", WindowProduct)
        self.ui.stackedWidget_content.setCurrentWidget(window.ui)
        self.setWindowTitle("ADITIM Monitor - Изделия")
        window.start_auto_refresh()

    def show_tasks(self):
        """Показать задачи"""
        self._stop_all_timers(except_this="task")
        window = self._ensure_window_created("window_task", WindowTask)
        self.ui.stackedWidget_content.setCurrentWidget(window.ui)
        self.setWindowTitle("ADITIM Monitor - Задачи")
        window.start_auto_refresh()

    def show_machines(self):
        """Показать станки"""
        self._stop_all_timers(except_this="machine")
        window = self._ensure_window_created("window_machine", WindowMachine)
        self.ui.stackedWidget_content.setCurrentWidget(window.ui)
        self.setWindowTitle("ADITIM Monitor - Станки")
        window.start_auto_refresh()

    def show_blanks(self):
        """Показать заготовки"""
        self._stop_all_timers()
        QMessageBox.information(self, "Заготовки", "Окно заготовок (в разработке)")

    def show_settings(self):
        """Показать настройки"""
        self._stop_all_timers()
        QMessageBox.information(self, "Настройки", "Настройки (в разработке)")

    def show_reports(self):
        """Показать отчеты"""
        self._stop_all_timers()
        QMessageBox.information(self, "Отчеты", "Отчеты (в разработке)")