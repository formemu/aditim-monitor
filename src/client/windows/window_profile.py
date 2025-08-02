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
from ..async_util import run_async


class WindowProfile(QWidget):
    """Виджет содержимого профилей"""

    def __init__(self):
        super().__init__()
        self.api_profile = ApiProfile()
        self.api_profile_tool = ApiProfileTool()
        self.current_profile_data = None  # Кэш данных профилей (None для первой загрузки)
        self.selected_row = None  # Запоминаем выбранную строку
        self.load_ui()
        self.setup_ui()
        # Не загружаем сразу, пусть таймер сработает первый раз

    def load_ui(self):
        """Загрузка UI из файла"""
        ui_file = QFile(UI_PATHS["PROFILE_CONTENT"])
        ui_file.open(QFile.ReadOnly)
        
        loader = QUiLoader()
        self.ui = loader.load(ui_file)
        ui_file.close()

    def setup_ui(self):
        """Настройка UI компонентов после загрузки"""
        # Применяем стили к виджету
        style_path = get_style_path("MAIN")
        style_sheet = load_styles_with_constants(style_path)
        self.ui.setStyleSheet(style_sheet)
        
        # Загружаем логотип ADITIM
        self.load_logo()
        
        self.ui.pushButton_profile_add.clicked.connect(self.on_add_clicked)
        self.ui.pushButton_profile_edit.clicked.connect(self.on_edit_clicked)
        self.ui.pushButton_profile_delete.clicked.connect(self.on_delete_clicked)
        self.ui.pushButton_sketch_open.clicked.connect(self.on_sketch_open_clicked)
        self.ui.pushButton_autocad_open.clicked.connect(self.on_autocad_open_clicked)
        self.ui.tableWidget_profiles.itemSelectionChanged.connect(self.on_selection_changed)
        self.ui.lineEdit_search.textChanged.connect(self.on_search_changed)
        
        # Настройка режима выделения таблицы
        self.ui.tableWidget_profiles.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ui.tableWidget_profiles.setSelectionMode(QAbstractItemView.SingleSelection)
        self.ui.tableWidget_profiles.setFocusPolicy(Qt.NoFocus)
        
        
        # Настройка ширины колонок
        self.ui.tableWidget_profiles.setColumnWidth(0, 150)  # Артикул - фиксированная ширина
        self.ui.tableWidget_profiles.horizontalHeader().setStretchLastSection(True)  # Описание - растягивается
        
        # Настройка автоматического обновления каждые 5 секунд с умной проверкой
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.load_profile)
        # НЕ запускаем таймер сразу, он будет запущен при активации окна
        # self.update_timer.start(5000)  # 5000 мс = 5 секунд

    def load_logo(self):
        """Загружает логотип ADITIM в правую панель"""
        try:
            # Путь к основному логотипу ADITIM - используем абсолютный путь
            logo_path = ICON_PATHS["ADITIM_LOGO_MAIN"]
            
            print(f"Загружаем логотип из: {logo_path}")
            
            if os.path.exists(logo_path):
                # Загружаем изображение
                pixmap = QPixmap(logo_path)
                
                if not pixmap.isNull():
                    # Масштабируем с сохранением пропорций для компактного размера 300x100
                    scaled_pixmap = pixmap.scaled(300, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    
                    # Устанавливаем изображение в QLabel
                    self.ui.label_logo.setPixmap(scaled_pixmap)
                    self.ui.label_logo.setText("")  # Убираем текст "ADITIM"
                    print("Логотип загружен успешно")
                else:
                    print("Ошибка: QPixmap не смог загрузить изображение (файл поврежден или неподдерживаемый формат)")
                    self.ui.label_logo.setText("ADITIM\nЛОГОТИП")
                    
                # Устанавливаем темный фон для лучшего контраста с белым логотипом

            else:
                # Если файл не найден, оставляем текст
                self.ui.label_logo.setText("ADITIM\nЛОГОТИП")
                print(f"Файл логотипа не найден: {logo_path}")
                
        except Exception as e:
            print(f"Ошибка загрузки логотипа: {e}")
            self.ui.label_logo.setText("ADITIM\nЛОГОТИП")

    def on_add_clicked(self):
        """Добавление нового профиля"""
        try:
            # Создаем диалог создания профиля
            dialog = DialogCreateProfile(self)
            
            # Подключаем сигнал успешного создания профиля
            dialog.profile_created.connect(self.on_profile_created)
            
            # Показываем диалог
            dialog.exec()
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось открыть диалог создания профиля: {e}")

    def on_profile_created(self, profile_data):
        """Обработчик успешного создания профиля"""
        try:
            # Принудительно перезагружаем список профилей с сервера
            self.current_profile_data = []  # Сбрасываем кэш для принудительного обновления
            self.load_profile_from_server()
            
            # Находим и выделяем новый профиль в таблице
            for row in range(self.ui.tableWidget_profiles.rowCount()):
                article_item = self.ui.tableWidget_profiles.item(row, 0)
                if article_item and article_item.text() == profile_data.get('article', ''):
                    self.ui.tableWidget_profiles.selectRow(row)
                    break
                    
        except Exception as e:
            QMessageBox.warning(self, "Предупреждение", f"Профиль создан, но не удалось обновить список: {e}")

    def refresh_data(self):
        """Публичный метод для принудительного обновления данных"""
        self.current_profile_data = []  # Сбрасываем кэш
        self.load_profile_from_server()

    def load_profile_from_server(self):
        """Загружает профили с сервера"""
        try:
            profile = self.api_profile.get_profile()
            self.update_profile_table(profile)
        except Exception as e:
            QMessageBox.warning(self, "Предупреждение", f"Не удалось загрузить профили с сервера: {e}")

    def update_profile_table(self, profiles):
        """Обновляет таблицу профилей с проверкой изменений"""
        # Проверяем если таблица пустая - обновляем принудительно
        is_table_empty = self.ui.tableWidget_profiles.rowCount() == 0
        
        # Сравниваем новые данные с кэшем (None означает первую загрузку)
        if self.current_profile_data is not None and profiles == self.current_profile_data and not is_table_empty:
            return  # Данные не изменились и таблица не пустая, не обновляем
        
        # Сохраняем текущее выделение
        current_selection = None
        selected_items = self.ui.tableWidget_profiles.selectedItems()
        if selected_items:
            current_selection = selected_items[0].row()
        
        # Обновляем кэш
        self.current_profile_data = profiles
        
        # Очищаем таблицу
        self.ui.tableWidget_profiles.setRowCount(0)
        
        # Заполняем таблицу данными с сервера
        self.ui.tableWidget_profiles.setRowCount(len(profiles))
        
        for row, profile in enumerate(profiles):
            # Артикул
            article_item = QTableWidgetItem(profile.get('article', ''))
            article_item.setFlags(article_item.flags() & ~Qt.ItemIsEditable)
            self.ui.tableWidget_profiles.setItem(row, 0, article_item)
            
            # Описание
            description_item = QTableWidgetItem(profile.get('description', ''))
            description_item.setFlags(description_item.flags() & ~Qt.ItemIsEditable)
            self.ui.tableWidget_profiles.setItem(row, 1, description_item)
        
        # Восстанавливаем выделение если возможно
        if current_selection is not None and current_selection < len(profiles):
            self.ui.tableWidget_profiles.selectRow(current_selection)
            self.selected_row = current_selection

    def load_profile(self):
        """загрузка профилей с сервера"""
        try:
            profile = self.api_profile.get_profile()
            self.update_profile_table(profile)
        except Exception as e:
            print(f"Ошибка загрузки профилей: {e}")

    def on_edit_clicked(self):
        """Редактирование профиля"""
        QMessageBox.information(self, "Редактировать", "Редактирование профиля")

    def on_delete_clicked(self):
        """Удаление профиля с подтверждением и опцией удаления инструментов"""
        selected_items = self.ui.tableWidget_profiles.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Удаление профиля", "Сначала выберите профиль для удаления.")
            return

        row = selected_items[0].row()
        profile = None
        if self.current_profile_data and row < len(self.current_profile_data):
            profile = self.current_profile_data[row]
        if not profile:
            QMessageBox.warning(self, "Удаление профиля", "Не удалось получить данные профиля.")
            return

        article = profile.get('article', '-')
        description = profile.get('description', '-')

        # Подтверждение удаления профиля
        reply = QMessageBox.question(
            self,
            "Удалить профиль",
            f"Вы действительно хотите удалить профиль?\nАртикул: {article}\nОписание: {description}",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return

        # Спросить про удаление инструментов
        delete_tools = False
        reply_tools = QMessageBox.question(
            self,
            "Удалить инструменты?",
            "Удалить все инструменты, связанные с этим профилем?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply_tools == QMessageBox.Yes:
            delete_tools = True

        try:
            # Удаляем инструменты и их компоненты, если выбрано
            if delete_tools:
                # Получаем все инструменты профиля
                tools = self.api_profile_tool.get_profile_tool()
                profile_tool = [t for t in tools if t.get('profile_id') == profile['id']]
                for tool in profile_tool:
                    # Удаляем компоненты инструмента
                    self.api_profile_tool.delete_profile_tool_component(tool['id'])
                # Удаляем инструменты профиля
                self.api_profile_tool.delete_profile_tool(profile['id'])
            # Удаляем сам профиль
            self.api_profile.delete_profile(profile['id'])
            QMessageBox.information(self, "Удаление", "Профиль успешно удалён.")
            self.refresh_data()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось удалить профиль: {e}")

    def on_sketch_open_clicked(self):
        """Открытие эскиза"""
        QMessageBox.information(self, "Эскиз", "Открытие эскиза")

    def on_autocad_open_clicked(self):
        """Открытие чертежа в AutoCAD"""
        QMessageBox.information(self, "AutoCAD", "Открытие в AutoCAD")

    def on_selection_changed(self):
        """Изменение выбранного профиля"""
        selected_items = self.ui.tableWidget_profiles.selectedItems()
        if selected_items:
            row = selected_items[0].row()
            self.selected_row = row  # Запоминаем выбранную строку
            self.ui.pushButton_sketch_open.setEnabled(True)
            self.ui.pushButton_autocad_open.setEnabled(True)
            # Обновляем информацию в панели предварительного просмотра
            article = self.ui.tableWidget_profiles.item(row, 0).text()
            description = self.ui.tableWidget_profiles.item(row, 1).text() if self.ui.tableWidget_profiles.item(row, 1) else ""
            self.ui.label_profile_article.setText(f"Артикул: {article}")
            self.ui.label_profile_description.setText(f"Описание: {description}")

            # Подгружаем и отображаем эскиз профиля
            profile = None
            if self.current_profile_data and row < len(self.current_profile_data):
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

    def load_and_show_sketch(self, profile):
        """Загружает и отображает эскиз профиля или иконку-заглушку"""
        if profile and profile.get('sketch'):
            try:
                sketch_data = profile['sketch']
                if sketch_data.startswith('data:image'):
                    base64_data = sketch_data.split(',')[1]
                else:
                    base64_data = sketch_data
                image_data = base64.b64decode(base64_data)
                pixmap = QPixmap()
                if pixmap.loadFromData(image_data) and not pixmap.isNull():
                    scaled_pixmap = pixmap.scaled(200, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    self.ui.label_sketch.setPixmap(scaled_pixmap)
                    self.ui.label_sketch.setText("")
                else:
                    self.set_sketch_placeholder()
                    self.ui.label_sketch.setText("Ошибка загрузки эскиза")
            except Exception:
                self.set_sketch_placeholder()
                self.ui.label_sketch.setText("Ошибка загрузки эскиза")
        else:
            self.set_sketch_placeholder()
            self.ui.label_sketch.setText("Эскиз не найден")

    def set_sketch_placeholder(self):
        """Устанавливает иконку-заглушку вместо эскиза"""
        placeholder_path = ICON_PATHS.get("SKETCH_PLACEHOLDER")
        if placeholder_path and os.path.exists(placeholder_path):
            pixmap = QPixmap(placeholder_path)
            scaled_pixmap = pixmap.scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.ui.label_sketch.setPixmap(scaled_pixmap)
        else:
            self.ui.label_sketch.clear()

    def on_search_changed(self, text):
        """Поиск по артикулу"""
        # Простая фильтрация по артикулу
        for row in range(self.ui.tableWidget_profiles.rowCount()):
            item = self.ui.tableWidget_profiles.item(row, 0)
            if item:
                visible = text.lower() in item.text().lower()
                self.ui.tableWidget_profiles.setRowHidden(row, not visible)

    def start_auto_refresh(self):
        """Запускает автоматическое обновление данных"""
        if not self.update_timer.isActive():
            self.update_timer.start(5000)  # 5 секунд
            # Сразу загружаем данные при активации
            self.load_profile()

    def stop_auto_refresh(self):
        """Останавливает автоматическое обновление данных"""
        if self.update_timer.isActive():
            self.update_timer.stop()
