"""Содержимое профилей для ADITIM Monitor Client"""
import base64
from PySide6.QtWidgets import QMessageBox
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from ..base_window import BaseWindow
from ..base_table import BaseTable
from ..constant import UI_PATHS_ABS
from ..widgets.profile.dialog_create_profile import DialogCreateProfile
from ..widgets.profile.dialog_edit_profile import DialogEditProfile
from ..api_manager import api_manager


class WindowProfile(BaseWindow):
    """Виджет содержимого профилей с таблицей, фильтрацией и просмотром эскизов"""
    def __init__(self):
        self.profile = None
        super().__init__(UI_PATHS_ABS["PROFILE_CONTENT"], api_manager)

    # =============================================================================
    # ИНИЦИАЛИЗАЦИЯ И ЗАГРУЗКА ИНТЕРФЕЙСА
    # =============================================================================
    def setup_ui(self):
        """Настройка UI компонентов"""
        self.apply_styles()
        self.load_logo()

        self.ui.pushButton_profile_add.clicked.connect(self.on_profile_add_clicked)
        self.ui.pushButton_profile_edit.clicked.connect(self.on_profile_edit_clicked)
        self.ui.pushButton_profile_delete.clicked.connect(self.on_profile_delete_clicked)
        self.ui.lineEdit_search.textChanged.connect(self.filter_table)
        self.ui.tableWidget_profile.itemClicked.connect(self.on_main_table_clicked)

        self.refresh_data()

    # =============================================================================
    # УПРАВЛЕНИЕ ДАННЫМИ: ЗАГРУЗКА И ОБНОВЛЕНИЕ
    # =============================================================================
    def refresh_data(self):
        """Обновление данных в виджете"""
        self.profile = None
        self.clear_info_panel()
        self.update_profile_table()

    def update_profile_table(self):
        """Обновление таблицы профилей"""
        BaseTable.populate_table(
            self.ui.tableWidget_profile,
            ["Артикул", "Описание"],
            api_manager.table["profile"],
            func_row_mapper=lambda p: [p['article'], p['description']],
            func_id_getter=lambda p: p['id']
        )

    def update_profile_info_panel(self):
        """Обновление панели профиля"""
        self.ui.label_profile_article.setText(f"Артикул: {self.profile['article']}")
        self.ui.label_profile_description.setText(f"Описание: {self.profile['description']}")
        sketch_data = self.profile["sketch"]
        self.load_and_show_sketch(sketch_data)

    def clear_info_panel(self):
        """Очистка панели информации о профиле"""
        self.ui.label_profile_article.setText("Артикул: -")
        self.ui.label_profile_description.setText("Описание: -")
        self.ui.label_sketch.setText("Эскиз отсутствует")

    def load_and_show_sketch(self, sketch_data):
        """Отображение эскиза профиля"""
        if sketch_data:
            base64_str = sketch_data.split(",", 1)[1] if "," in sketch_data else sketch_data
            image_data = base64.b64decode(base64_str)
            pixmap = QPixmap()
            if pixmap.loadFromData(image_data) and not pixmap.isNull():
                scaled = pixmap.scaled(200, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.ui.label_sketch.setPixmap(scaled)
                self.ui.label_sketch.setText("")
            else:
                self.ui.label_sketch.setText("Ошибка изображения")

        else: self.ui.label_sketch.setText("Эскиз отсутствует")

    # =============================================================================
    # ОБРАБОТЧИКИ СОБЫТИЙ: УПРАВЛЕНИЕ
    # =============================================================================
    def on_profile_add_clicked(self):
        """Открытие диалога добавления профиля"""
        dialog = DialogCreateProfile(self)
        dialog.exec()
        QMessageBox.warning(self, "Внимание", "Профиль добавлен")

    def on_profile_edit_clicked(self):
        """Редактирование профиля"""
        if self.profile:
            dialog = DialogEditProfile(self.profile, self)
            dialog.exec()
            QMessageBox.warning(self, "Внимание", "Данные о профиле обновлены")
        else: QMessageBox.warning(self, "Внимание", "Выберите профиль для редактирования")

    def on_profile_delete_clicked(self):
        """Удаление профиля"""
        if self.profile:
            api_manager.api_profile.delete_profile(self.profile['id'])
            QMessageBox.warning(self, "Внимание", "Профиль удален")
        else: QMessageBox.warning(self, "Внимание", "Выберите профиль для удаления")

    # =============================================================================
    # ОБРАБОТЧИКИ СОБЫТИЙ: ВЫДЕЛЕНИЕ
    # =============================================================================
    def on_main_table_clicked(self):
        """Обработка выбора строки"""
        profile_id = BaseTable.get_selected_id(self.ui.tableWidget_profile)
        if profile_id is None:
            return
        self.profile = api_manager.get_by_id("profile", profile_id)
        self.update_profile_info_panel()

    # =============================================================================
    # ОБРАБОТЧИКИ ДОПОЛНИТЕЛЬНЫХ ДЕЙСТВИЙ
    # =============================================================================
    def filter_table(self):
        """Фильтрация по артикулу"""
        text = self.ui.lineEdit_search.text().strip().lower()
        table = self.ui.tableWidget_profile
        for row in range(table.rowCount()):
            item = table.item(row, 1)
            visible = not text or (item and text in item.text().lower())
            table.setRowHidden(row, not visible)