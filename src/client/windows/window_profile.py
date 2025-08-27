"""Содержимое профилей для ADITIM Monitor Client"""
import base64
from PySide6.QtWidgets import QWidget, QMessageBox, QTableWidgetItem, QAbstractItemView, QHeaderView, QDialog
from PySide6.QtCore import QFile, Qt, QTimer
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QPixmap
from ..constant import UI_PATHS_ABS as UI_PATHS, ICON_PATHS_ABS as ICON_PATHS, get_style_path
from ..widgets.dialog_create_profile import DialogCreateProfile
from ..widgets.dialog_edit_profile import DialogEditProfile
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
        # Подключение сигналов
        self.ui.pushButton_profile_add.clicked.connect(self.on_add_clicked)
        self.ui.pushButton_profile_edit.clicked.connect(self.on_edit_clicked)
        self.ui.pushButton_profile_delete.clicked.connect(self.on_delete_clicked)
        self.ui.pushButton_sketch_open.clicked.connect(self.on_sketch_open_clicked)
        self.ui.pushButton_autocad_open.clicked.connect(self.on_autocad_open_clicked)
        self.ui.tableWidget_profiles.itemSelectionChanged.connect(self.on_selection_changed)
        self.ui.lineEdit_search.textChanged.connect(self.filter_table)
        # Настройка таблицы
        table = self.ui.tableWidget_profiles
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setSelectionMode(QAbstractItemView.SingleSelection)
        table.setFocusPolicy(Qt.NoFocus)
        # Таймер автообновления
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.refresh_data)
    
    def load_logo(self):
        """Загрузка логотипа ADITIM"""
        logo_path = ICON_PATHS.get("ADITIM_LOGO_MAIN")
        pixmap = QPixmap(logo_path)
        scaled = pixmap.scaled(300, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.ui.label_logo.setPixmap(scaled)
        self.ui.label_logo.setText("")

    # =============================================================================
    # УПРАВЛЕНИЕ ДАННЫМИ: ЗАГРУЗКА И ОБНОВЛЕНИЕ
    # =============================================================================
    def refresh_data(self):
        """Принудительное обновление данных"""
        api_manager.refresh_profile_async()
        self.update_profile_table()
        if self.selected_row is not None:
            self.update_profile_info_panel()

    # =============================================================================
    # ОТОБРАЖЕНИЕ ДАННЫХ: ТАБЛИЦА ПРОФИЛЕЙ И ИНФОРМАЦИОННЫЕ ПАНЕЛИ
    # =============================================================================
    def update_profile_table(self):
        """Обновление таблицы профилей с корректным отображением и заполнением по ширине"""
        table = self.ui.tableWidget_profiles
        table.setRowCount(len(api_manager.profile))
        table.setColumnCount(2)
        # Заголовки столбцов
        table.setHorizontalHeaderLabels(["Артикул", "Описание"])
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        
        for row, profile in enumerate(api_manager.profile):
            article = profile['article']
            table.setItem(row, 0, QTableWidgetItem(article))
            description = profile['description']
            table.setItem(row, 1, QTableWidgetItem(description))
        
    def update_profile_info_panel(self):
        """Обновление панели информации о профиле"""
        self.profile = api_manager.profile[self.selected_row]
        article = self.profile['article']
        description = self.profile['description']
        self.load_and_show_sketch()
        self.ui.label_profile_article.setText(f"Артикул: {article}")
        self.ui.label_profile_description.setText(f"Описание: {description}")

    def clear_profile_info_panel(self):
        """Очистка панели информации о профиле"""
        self.ui.label_profile_article.setText("Артикул: -")
        self.ui.label_profile_description.setText("Описание: -")

    def load_and_show_sketch(self):
        """Отображение эскиза профиля"""
        sketch_data = self.profile['sketch']
        if not sketch_data:
            self.ui.label_sketch.setText("Эскиз отсутствует")
            return
        base64_data = sketch_data.split(',')[1] if sketch_data.startswith('data:image') else sketch_data
        image_data = base64.b64decode(base64_data)
        pixmap = QPixmap()
        if pixmap.loadFromData(image_data) and not pixmap.isNull():
            scaled = pixmap.scaled(200, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.ui.label_sketch.setPixmap(scaled)
            self.ui.label_sketch.setText("")

    # =============================================================================
    # ОБРАБОТЧИКИ СОБЫТИЙ: УПРАВЛЕНИЕ ПРОФИЛЯМИ
    # =============================================================================
    def on_add_clicked(self):
        """Открытие диалога добавления профиля"""
        dialog = DialogCreateProfile(self)
        if dialog.exec() == QDialog.Accepted:
            self.refresh_data()

    def on_edit_clicked(self):
        """Редактирование профиля"""
        dialog = DialogEditProfile(self.profile, self)
        if dialog.exec() == QDialog.Accepted:
            self.refresh_data()

    def on_delete_clicked(self):
        """Удаление профиля с подтверждением и опцией удаления инструментов"""
        api_manager.api_profile.delete_profile(self.profile['id'])
        self.refresh_data()

    def get_selected_row(self):
        """Возвращает индекс выбранной строки или None"""
        selected = self.ui.tableWidget_profiles.selectedItems()
        if selected:
            return selected[0].row()
        else:
            return None

    # =============================================================================
    # ОБРАБОТЧИКИ СОБЫТИЙ: ВЫДЕЛЕНИЕ И ПОИСК
    # =============================================================================
    def on_selection_changed(self):
        """Обработка выбора строки"""
        self.selected_row = self.get_selected_row()
        if self.selected_row is not None:
            self.update_profile_info_panel()
        else:
            self.selected_row = None
            self.clear_profile_info_panel()

    def filter_table(self):
        """Фильтрация строк таблицы по тексту в первом столбце"""
        table = self.ui.tableWidget_profiles
        text = self.ui.lineEdit_search.text().lower()
        for row in range(table.rowCount()):
            item = table.item(row, 0)
            visible = item and text in item.text().lower()
            table.setRowHidden(row, not visible)

    # =============================================================================
    # ОБРАБОТЧИКИ ДОПОЛНИТЕЛЬНЫХ ДЕЙСТВИЙ
    # =============================================================================
    def on_sketch_open_clicked(self):
        """Открытие эскиза"""
        QMessageBox.information(self, "Эскиз", "Открытие эскиза")

    def on_autocad_open_clicked(self):
        """Открытие чертежа в AutoCAD"""
        QMessageBox.information(self, "AutoCAD", "Открытие в AutoCAD")

    # =============================================================================
    # УПРАВЛЕНИЕ АВТООБНОВЛЕНИЕМ
    # =============================================================================
    def start_auto_refresh(self):
        """Запуск автообновления"""
        if not self.update_timer.isActive():
            self.update_timer.start(5000)
            self.refresh_data()

    def stop_auto_refresh(self):
        """Остановка автообновления"""
        if self.update_timer.isActive():
            self.update_timer.stop()