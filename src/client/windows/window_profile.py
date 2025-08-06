"""
Содержимое профилей для ADITIM Monitor Client
"""
import os
import base64
from PySide6.QtWidgets import QWidget, QMessageBox, QTableWidgetItem, QAbstractItemView, QHeaderView
from PySide6.QtCore import QFile, Qt, QTimer
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QPixmap
from ..constant import UI_PATHS_ABS as UI_PATHS, ICON_PATHS_ABS as ICON_PATHS, get_style_path
from ..widgets.dialog_create_profile import DialogCreateProfile
from ..api.api_profile import ApiProfile
from ..api.api_profile_tool import ApiProfileTool
from ..style_util import load_styles


class WindowProfile(QWidget):
    """Виджет содержимого профилей с таблицей, фильтрацией и просмотром эскизов"""
    def __init__(self):
        super().__init__()
        self.api_profile = ApiProfile()
        self.api_profile_tool = ApiProfileTool()
        self.profile_data = None  # Кэш данных профилей
        self.selected_row = None  # Индекс выбранной строки
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
        self.ui.lineEdit_search.textChanged.connect(lambda text: self._filter_table(self.ui.tableWidget_profiles, text.lower()))
        # Настройка таблицы
        table = self.ui.tableWidget_profiles
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setSelectionMode(QAbstractItemView.SingleSelection)
        table.setFocusPolicy(Qt.NoFocus)
        # Таймер автообновления
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.load_data_from_server)
    
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
        self.profile_data = []
        self.load_data_from_server()

    def load_data_from_server(self):
        """Загрузка профилей с сервера"""
        self.profile_data = self.api_profile.get_profile()
        self.update_profile_table(self.profile_data)

    # =============================================================================
    # ОТОБРАЖЕНИЕ ДАННЫХ: ТАБЛИЦА ПРОФИЛЕЙ И ИНФОРМАЦИОННЫЕ ПАНЕЛИ
    # =============================================================================
    def update_profile_table(self, list_profile):
        """Обновление таблицы профилей с корректным отображением и заполнением по ширине"""
        table = self.ui.tableWidget_profiles
        table.setRowCount(len(list_profile))
        table.setColumnCount(2)
        # Заголовки столбцов
        table.setHorizontalHeaderLabels(["Артикул", "Описание"])
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        for row, profile in enumerate(list_profile):
            article = profile.get('article', '')
            table.setItem(row, 0, QTableWidgetItem(article))
            description = profile.get('description', '')
            table.setItem(row, 1, QTableWidgetItem(description))
        
    def update_profile_info_panel(self, profile):
        """Обновление панели информации о профиле"""
        article = profile.get('article')
        description = profile.get('description')
        self.load_and_show_sketch(profile)
        self.ui.label_profile_article.setText(f"Артикул: {article}")
        self.ui.label_profile_description.setText(f"Описание: {description}")

    def clear_profile_info_panel(self):
        """Очистка панели информации о профиле"""
        self.ui.label_profile_article.setText("Артикул: -")
        self.ui.label_profile_description.setText("Описание: -")

    def set_sketch_placeholder(self):
        """Установка иконки-заглушки для эскиза"""
        placeholder_path = ICON_PATHS.get("SKETCH_PLACEHOLDER")
        if placeholder_path and os.path.exists(placeholder_path):
            pixmap = QPixmap(placeholder_path)
            scaled = pixmap.scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.ui.label_sketch.setPixmap(scaled)
        else:
            self.ui.label_sketch.clear()

    def load_and_show_sketch(self, profile):
        """Отображение эскиза профиля"""
        if not profile or not profile.get('sketch'):
            self.set_sketch_placeholder()
            self.ui.label_sketch.setText("Эскиз не найден")
            return
        sketch_data = profile['sketch']
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
        dialog.profile_created.connect(self.refresh_data)
        dialog.exec()

    def on_edit_clicked(self):
        """Редактирование профиля"""
        QMessageBox.information(self, "Редактировать", "Редактирование профиля")

    def on_delete_clicked(self):
        """Удаление профиля с подтверждением и опцией удаления инструментов"""
        row = self._get_selected_row()
        profile = self.profile_data[row]
        self.delete_profile_tools(profile['id'])
        self.api_profile.delete_profile(profile['id'])
        self.refresh_data()

    def get_selected_row(self):
        """Возвращает индекс выбранной строки или None"""
        selected = self.ui.tableWidget_profiles.selectedItems()
        return selected[0].row() if selected else None

    def delete_profile_tools(self, profile_id):
        """Удаляет инструменты и их компоненты для профиля"""
        tools = self.api_profile_tool.get_profile_tool()
        profile_tools = [t for t in tools if t.get('profile_id') == profile_id]
        for tool in profile_tools:
            self.api_profile_tool.delete_profile_tool_component(tool['id'])
        self.api_profile_tool.delete_profile_tool(profile_id)

    # =============================================================================
    # ОБРАБОТЧИКИ СОБЫТИЙ: ВЫДЕЛЕНИЕ И ПОИСК
    # =============================================================================
    def on_selection_changed(self):
        """Обработка выбора строки"""
        row = self.get_selected_row()
        if row is not None:
            self.selected_row = row
            profile = self.profile_data[row]
            self.update_profile_info_panel(profile)
        else:
            self.selected_row = None
            self.clear_profile_info_panel()

    def filter_table(self, table, text):
        """Фильтрация строк таблицы по тексту в первом столбце"""
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
            self.load_data_from_server()

    def stop_auto_refresh(self):
        """Остановка автообновления"""
        if self.update_timer.isActive():
            self.update_timer.stop()