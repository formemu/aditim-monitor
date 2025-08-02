"""
Содержимое профилей для ADITIM Monitor Client
"""
import os
import base64
from PySide6.QtWidgets import QWidget, QMessageBox, QTableWidgetItem, QAbstractItemView
from PySide6.QtCore import QFile, Qt, QTimer
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QPixmap
from ..constant import UI_PATHS_ABS as UI_PATHS, ICON_PATHS_ABS as ICON_PATHS, get_style_path
from ..widgets.dialog_create_profile import DialogCreateProfile
from ..api.api_profile import ApiProfile
from ..api.api_profile_tool import ApiProfileTool
from ..style_util import load_styles_with_constants


class WindowProfile(QWidget):
    """Виджет содержимого профилей с таблицей, фильтрацией и просмотром эскизов"""
    def __init__(self):
        super().__init__()
        self.api_profile = ApiProfile()
        self.api_profile_tool = ApiProfileTool()
        self.current_profile_data = None  # Кэш данных профилей
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
        self.ui.setStyleSheet(load_styles_with_constants(get_style_path("MAIN")))
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
        table.setColumnWidth(0, 150)  # Артикул
        table.horizontalHeader().setStretchLastSection(True)  # Описание
        # Таймер автообновления
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.load_data_from_server)

    # =============================================================================
    # РАБОТА С ЛОГОТИПОМ И ЭСКИЗАМИ
    # =============================================================================
    def load_logo(self):
        """Загрузка логотипа ADITIM"""
        logo_path = ICON_PATHS.get("ADITIM_LOGO_MAIN")
        try:
            if os.path.exists(logo_path):
                pixmap = QPixmap(logo_path)
                if not pixmap.isNull():
                    scaled = pixmap.scaled(300, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    self.ui.label_logo.setPixmap(scaled)
                    self.ui.label_logo.setText("")
                    return
            self.ui.label_logo.setText("ADITIM\nЛОГОТИП")
        except Exception as e:
            print(f"Ошибка загрузки логотипа: {e}")
            self.ui.label_logo.setText("ADITIM\nЛОГОТИП")

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
        try:
            image_data = base64.b64decode(base64_data)
            pixmap = QPixmap()
            if pixmap.loadFromData(image_data) and not pixmap.isNull():
                scaled = pixmap.scaled(200, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.ui.label_sketch.setPixmap(scaled)
                self.ui.label_sketch.setText("")
            else:
                self._set_sketch_error()
        except Exception:
            self._set_sketch_error()

    def _set_sketch_error(self):
        """Установка заглушки при ошибке загрузки эскиза"""
        self.set_sketch_placeholder()
        self.ui.label_sketch.setText("Ошибка загрузки эскиза")

    # =============================================================================
    # УПРАВЛЕНИЕ ДАННЫМИ: ЗАГРУЗКА И ОБНОВЛЕНИЕ
    # =============================================================================
    def refresh_data(self):
        """Принудительное обновление данных"""
        self.current_profile_data = []
        self.load_data_from_server()

    def load_data_from_server(self):
        """Загрузка профилей с сервера"""
        try:
            profiles = self.api_profile.get_profile()
            self.update_profile_table(profiles)
        except Exception as e:
            QMessageBox.warning(self, "Предупреждение", f"Ошибка загрузки: {e}")

    # =============================================================================
    # ОТОБРАЖЕНИЕ ДАННЫХ: ТАБЛИЦА ПРОФИЛЕЙ
    # =============================================================================
    def update_profile_table(self, profiles):
        """Обновление таблицы с защитой от дублей"""
        if self._should_skip_update(self.current_profile_data, profiles):
            return
        self.current_profile_data = profiles
        self._update_table_with_selection(
            table=self.ui.tableWidget_profiles,
            data=profiles,
            columns=[lambda p: p.get('article', ''), lambda p: p.get('description', '')]
        )

    def _should_skip_update(self, current_data, new_data):
        """Проверка, нужно ли обновлять таблицу"""
        is_empty = self.ui.tableWidget_profiles.rowCount() == 0
        return current_data is not None and new_data == current_data and not is_empty

    def _update_table_with_selection(self, table, data, columns):
        """Обновляет таблицу и восстанавливает выделение"""
        prev_selection = self.selected_row
        table.setRowCount(0)
        table.setRowCount(len(data))
        for row, item in enumerate(data):
            for col_idx, getter in enumerate(columns):
                cell = QTableWidgetItem(getter(item))
                cell.setFlags(cell.flags() & ~Qt.ItemIsEditable)
                table.setItem(row, col_idx, cell)
        if prev_selection is not None and prev_selection < len(data):
            table.selectRow(prev_selection)

    # =============================================================================
    # ОБРАБОТЧИКИ СОБЫТИЙ: УПРАВЛЕНИЕ ПРОФИЛЯМИ
    # =============================================================================
    def on_add_clicked(self):
        """Открытие диалога добавления профиля"""
        self._open_dialog(DialogCreateProfile, 'profile_created', self.on_profile_created)

    def on_profile_created(self, profile_data):
        """Обработка создания профиля"""
        self.refresh_data()
        self._select_row_by_text(profile_data.get('article', ''))

    def _open_dialog(self, dialog_class, signal_name, callback):
        """Унифицированное открытие диалога"""
        try:
            dialog = dialog_class(self)
            getattr(dialog, signal_name).connect(callback)
            dialog.exec()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось открыть диалог: {e}")

    def _select_row_by_text(self, text):
        """Выделяет строку по тексту в первом столбце"""
        for row in range(self.ui.tableWidget_profiles.rowCount()):
            item = self.ui.tableWidget_profiles.item(row, 0)
            if item and item.text() == text:
                self.ui.tableWidget_profiles.selectRow(row)
                break

    def on_edit_clicked(self):
        """Редактирование профиля"""
        QMessageBox.information(self, "Редактировать", "Редактирование профиля")

    def on_delete_clicked(self):
        """Удаление профиля с подтверждением и опцией удаления инструментов"""
        row = self._get_selected_row()
        if row is None:
            QMessageBox.warning(self, "Удаление", "Выберите профиль для удаления.")
            return
        profile = self.current_profile_data[row]
        article = profile.get('article', '-')
        desc = profile.get('description', '-')
        if not self._confirm_deletion(article, desc):
            return
        delete_tools = self._confirm_delete_tools()
        try:
            if delete_tools:
                self._delete_profile_tools(profile['id'])
            self.api_profile.delete_profile(profile['id'])
            QMessageBox.information(self, "Удаление", "Профиль успешно удалён.")
            self.refresh_data()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось удалить профиль: {e}")

    def _get_selected_row(self):
        """Возвращает индекс выбранной строки или None"""
        selected = self.ui.tableWidget_profiles.selectedItems()
        return selected[0].row() if selected else None

    def _confirm_deletion(self, article, description):
        """Запрос подтверждения удаления профиля"""
        reply = QMessageBox.question(
            self, "Удалить профиль",
            f"Удалить профиль?\nАртикул: {article}\nОписание: {description}",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        return reply == QMessageBox.Yes

    def _confirm_delete_tools(self):
        """Запрос на удаление связанных инструментов"""
        reply = QMessageBox.question(
            self, "Удалить инструменты?",
            "Удалить все инструменты, связанные с этим профилем?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        return reply == QMessageBox.Yes

    def _delete_profile_tools(self, profile_id):
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
        row = self._get_selected_row()
        if row is not None:
            self.selected_row = row
            self.ui.pushButton_sketch_open.setEnabled(True)
            self.ui.pushButton_autocad_open.setEnabled(True)
            item = self.ui.tableWidget_profiles.item(row, 0)
            desc_item = self.ui.tableWidget_profiles.item(row, 1)
            self.ui.label_profile_article.setText(f"Артикул: {item.text()}")
            self.ui.label_profile_description.setText(f"Описание: {desc_item.text() if desc_item else ''}")
            profile = self.current_profile_data[row]
            self.load_and_show_sketch(profile)
        else:
            self.selected_row = None
            self.ui.pushButton_sketch_open.setEnabled(False)
            self.ui.pushButton_autocad_open.setEnabled(False)
            self.ui.label_profile_article.setText("Артикул: -")
            self.ui.label_profile_description.setText("Описание: -")
            self.set_sketch_placeholder()
            self.ui.label_sketch.setText("")

    def _filter_table(self, table, text):
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