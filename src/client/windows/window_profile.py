"""Содержимое профилей для ADITIM Monitor Client"""
import base64
from PySide6.QtWidgets import QWidget, QMessageBox, QTableWidgetItem, QAbstractItemView, QHeaderView
from PySide6.QtCore import QFile, Qt
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QPixmap
from ..constant import UI_PATHS_ABS as UI_PATHS, ICON_PATHS_ABS as ICON_PATHS, get_style_path
from ..widgets.profile.dialog_create_profile import DialogCreateProfile
from ..widgets.profile.dialog_edit_profile import DialogEditProfile
from ..api_manager import api_manager
from ..style_util import load_styles


class WindowProfile(QWidget):
    """Виджет содержимого профилей с таблицей, фильтрацией и просмотром эскизов"""
    def __init__(self):
        super().__init__()
        self.profile = None
        self.selected_row = None
        self.load_ui()
        self.setup_ui()
        self.connect_signals()

    # =============================================================================
    # ИНИЦИАЛИЗАЦИЯ И ЗАГРУЗКА ИНТЕРФЕЙСА
    # =============================================================================

    def load_ui(self):
        """Загрузка UI из файла"""
        ui_file = QFile(UI_PATHS["PROFILE_CONTENT"])
        ui_file.open(QFile.ReadOnly)
        loader = QUiLoader()
        self.ui = loader.load(ui_file)
        ui_file.close()

    def setup_ui(self):
        """Настройка UI компонентов"""
        self.ui.setStyleSheet(load_styles(get_style_path("MAIN")))
        self.load_logo()

        # Кнопки
        self.ui.pushButton_profile_add.clicked.connect(self.on_add_clicked)
        self.ui.pushButton_profile_edit.clicked.connect(self.on_edit_clicked)
        self.ui.pushButton_profile_delete.clicked.connect(self.on_delete_clicked)
        self.ui.pushButton_sketch_open.clicked.connect(self.on_sketch_open_clicked)
        self.ui.pushButton_autocad_open.clicked.connect(self.on_autocad_open_clicked)

        # Таблица
        table = self.ui.tableWidget_profiles
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setSelectionMode(QAbstractItemView.SingleSelection)
        table.setFocusPolicy(Qt.NoFocus)

        # Поиск
        self.ui.lineEdit_search.textChanged.connect(self.filter_table)

        # Выбор строки
        table.itemSelectionChanged.connect(self.on_selection_changed)

        # Инициализация таблицы
        self.update_profile_table()

    def connect_signals(self):
        """Подключаемся к сигналам ApiManager"""
        api_manager.data_updated.connect(self.on_data_updated)

    def on_data_updated(self, group: str, key: str, success: bool):
        """Реакция на обновление данных"""
        if success and group == "table" and key == "profile":
            self.update_profile_table()
            if self.selected_row:
                self.update_profile_info_panel()

    def load_logo(self):
        """Загрузка логотипа ADITIM"""
        logo_path = ICON_PATHS.get("ADITIM_LOGO_MAIN")
        pixmap = QPixmap(logo_path)
        scaled = pixmap.scaled(300, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.ui.label_logo.setPixmap(scaled)
        self.ui.label_logo.setText("")

    # =============================================================================
    # ОТОБРАЖЕНИЕ ДАННЫХ
    # =============================================================================

    def update_profile_table(self):
        """Обновление таблицы профилей"""
        profiles = api_manager.table.get("profile", [])
        table = self.ui.tableWidget_profiles
        table.setRowCount(len(profiles))
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["id", "Артикул", "Описание"])

        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)

        for row, profile in enumerate(profiles):
            table.setItem(row, 0, QTableWidgetItem(str(profile['id'])))
            table.setItem(row, 1, QTableWidgetItem(profile['article']))
            table.setItem(row, 2, QTableWidgetItem(profile.get('description', '')))

        table.setColumnHidden(0, True)
        self.filter_table()  # применяем текущий фильтр

    def update_profile_info_panel(self):
        """Обновление панели информации о профиле"""
        if self.selected_row >= 0:
            item = self.ui.tableWidget_profiles.item(self.selected_row, 0)
            if item:
                profile_id = int(item.text())
                self.profile = api_manager.get_by_id("profile", profile_id)
                if self.profile:
                    self.ui.label_profile_article.setText(f"Артикул: {self.profile['article']}")
                    self.ui.label_profile_description.setText(f"Описание: {self.profile.get('description', '-')}")

                    sketch_data = self.profile.get("sketch")
                    self.load_and_show_sketch(sketch_data)
                    return

        self.clear_profile_info_panel()

    def clear_profile_info_panel(self):
        """Очистка панели информации о профиле"""
        self.ui.label_profile_article.setText("Артикул: -")
        self.ui.label_profile_description.setText("Описание: -")
        self.ui.label_sketch.setText("Эскиз отсутствует")

    def load_and_show_sketch(self, sketch_data):
        """Отображение эскиза профиля"""
        if not sketch_data:
            self.ui.label_sketch.setText("Эскиз отсутствует")
            return

        try:
            base64_str = sketch_data.split(",", 1)[1] if "," in sketch_data else sketch_data
            image_data = base64.b64decode(base64_str)
            pixmap = QPixmap()
            if pixmap.loadFromData(image_data) and not pixmap.isNull():
                scaled = pixmap.scaled(200, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.ui.label_sketch.setPixmap(scaled)
                self.ui.label_sketch.setText("")
            else:
                self.ui.label_sketch.setText("Ошибка изображения")
        except Exception:
            self.ui.label_sketch.setText("Ошибка загрузки")

    # =============================================================================
    # ОБРАБОТЧИКИ СОБЫТИЙ: УПРАВЛЕНИЕ ПРОФИЛЯМИ
    # =============================================================================
    def on_add_clicked(self):
        """Открытие диалога добавления профиля"""
        dialog = DialogCreateProfile(self)
        dialog.exec()

    def on_edit_clicked(self):
        """Редактирование профиля"""
        if not self.profile:
            self.show_warning_dialog("Выберите профиль для редактирования")
            return
        dialog = DialogEditProfile(self.profile, self)
        dialog.exec()

    def on_delete_clicked(self):
        """Удаление профиля"""
        if self.profile:
            api_manager.api_profile.delete_profile(self.profile['id'])

    # =============================================================================
    # ОБРАБОТЧИКИ СОБЫТИЙ: ВЫДЕЛЕНИЕ И ПОИСК
    # =============================================================================
    def on_selection_changed(self):
        """Обработка выбора строки"""
        row = self.ui.tableWidget_profiles.currentRow()
        if row >= 0:
            self.selected_row = row
            self.update_profile_info_panel()
        else:
            self.selected_row = None
            self.clear_profile_info_panel()

    def filter_table(self):
        """Фильтрация по артикулу"""
        text = self.ui.lineEdit_search.text().strip().lower()
        table = self.ui.tableWidget_profiles
        for row in range(table.rowCount()):
            item = table.item(row, 1)
            visible = not text or (item and text in item.text().lower())
            table.setRowHidden(row, not visible)

    # =============================================================================
    # ОБРАБОТЧИКИ ДОПОЛНИТЕЛЬНЫХ ДЕЙСТВИЙ
    # =============================================================================

    def on_sketch_open_clicked(self):
        if self.profile:
            QMessageBox.information(self, "Эскиз", f"Открытие эскиза: {self.profile['article']}")

    def on_autocad_open_clicked(self):
        if self.profile:
            QMessageBox.information(self, "AutoCAD", f"Открытие в AutoCAD: {self.profile['article']}")

    def show_warning_dialog(self, message: str):
        QMessageBox.warning(self, "Внимание", message)