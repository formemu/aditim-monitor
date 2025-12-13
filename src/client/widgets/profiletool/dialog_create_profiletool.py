"""Диалог для создания инструмента профиля"""
from PySide6.QtWidgets import (QTableWidgetItem, QCheckBox, QAbstractItemView, QListWidgetItem)
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QPixmap
import base64

from ...base_dialog import BaseDialog
from ...constant import UI_PATHS_ABS
from ...api_manager import api_manager


class DialogCreateProfileTool(BaseDialog):
    """Диалог для создания инструмента профиля с компонентами"""
    def __init__(self, parent=None):
        self.list_component_widget = []
        self.selected_profile = None
        super().__init__(UI_PATHS_ABS["DIALOG_CREATE_PROFILETOOL"], api_manager, parent)
        self.load_dimension()
        
        # Устанавливаем заголовок
        self.setWindowTitle("Создание инструмента профиля")
        self.setModal(True)
        
    def setup_ui(self):
        """Настраивает UI компонентов после загрузки"""
        # Подключаем обработчики кнопок
        self.ui.buttonBox.accepted.connect(self.accept)
        self.ui.buttonBox.rejected.connect(self.reject)
        # Подключаем поиск профилей
        self.ui.lineEdit_profile_search.textChanged.connect(self.on_profile_search_changed)
        self.ui.listWidget_profile_results.itemClicked.connect(self.on_profile_selected)
        self.ui.comboBox_dimension.currentIndexChanged.connect(self.on_dimension_changed)
        # Настройка таблицы компонентов
        self.ui.tableWidget_components.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ui.tableWidget_components.setSelectionMode(QAbstractItemView.SingleSelection)
        self.ui.tableWidget_components.horizontalHeader().setStretchLastSection(True)

        # Устанавливаем ширины колонок
        self.ui.tableWidget_components.setColumnWidth(0, 100)  # Использовать
        self.ui.tableWidget_components.setColumnWidth(1, 200)  # Тип компонента
        self.ui.tableWidget_components.setColumnWidth(2, 150)  # Статус

    # =============================================================================
    # Загрузка справочников и начальных данных
    # =============================================================================
    def load_dimension(self):
        """Загружает размерности по умолчанию"""
        self.ui.comboBox_dimension.clear()
        for dimension in api_manager.directory['profiletool_dimension']:
            name = dimension['name']
            self.ui.comboBox_dimension.addItem(name, dimension)

    # =============================================================================
    # Управление таблицей компонентов
    # =============================================================================

    def on_dimension_changed(self, index):
        """Обработчик изменения размерности"""
        dimension = self.ui.comboBox_dimension.itemData(index)
        self.setup_component_table(dimension)

    def setup_component_table(self, dimension):
        """Загружает типы компонентов в таблицу"""
        # Устанавливаем описание размерности в текстовое поле

        self.ui.textEdit_description.setText(dimension['description'])

        # Очищаем таблицу
        self.ui.tableWidget_components.setRowCount(0)
        self.list_component_widget.clear()
        # Фильтруем типы компонентов по выбранной размерности
        list_filtered_type = [
            type for type in api_manager.directory['component_type']
            if type['profiletool_dimension_id'] == dimension['id']
        ]
        self.ui.tableWidget_components.setRowCount(len(list_filtered_type))
        for row, type in enumerate(list_filtered_type):
            # Колонка 0: Checkbox "Использовать"
            checkbox = QCheckBox()
            checkbox.setChecked(True)
            self.ui.tableWidget_components.setCellWidget(row, 0, checkbox)
            # Колонка 1: Название типа компонента
            name_item = QTableWidgetItem(type['name'])
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
            name_item.setData(Qt.UserRole, type['id'])
            self.ui.tableWidget_components.setItem(row, 1, name_item)
            # Сохраняем ссылки на виджеты для удобного доступа
            self.list_component_widget.append({
                'type_id': type['id'],
                'checkbox': checkbox,
                'row': row
            })

    # =============================================================================
    # Управление поиском и выбором профиля
    # =============================================================================
    @Slot(str)
    def on_profile_search_changed(self, text):
        """Обработчик изменения поискового запроса"""
        self.ui.listWidget_profile_results.clear()
        # Ищем профили через api_manager
        search_results = api_manager.search_in('profile', 'article', text)
        for profile in search_results[:10]:  # Показываем максимум 10 результатов
            display_text = f"{profile['article']} - {profile.get('description', '')}"
            item = QListWidgetItem(display_text)
            # Сохраняем данные профиля в элементе списка
            item.setData(Qt.UserRole, profile)
            self.ui.listWidget_profile_results.addItem(item)

    @Slot(QListWidgetItem)
    def on_profile_selected(self, item):
        """Обработчик выбора профиля из списка"""
        profile = item.data(Qt.UserRole)
        if profile:
            self.selected_profile = profile
            # Обновляем поле поиска
            self.ui.lineEdit_profile_search.setText(profile['article'])
            # Скрываем список результатов
            self.ui.listWidget_profile_results.clear()
            # Загружаем эскиз профиля
            self.load_profile_sketch(profile)
            self.on_dimension_changed(0)
        else:
            pass

    def load_profile_sketch(self, profile):
        """Загружает и отображает эскиз профиля"""
        # Получаем данные профиля из api_manager
        if profile and profile['sketch']:
            # Конвертируем base64 в QPixmap
            sketch_data = profile['sketch']
            if sketch_data.startswith('data:image'):
                # Убираем префикс data:image/...;base64,
                base64_data = sketch_data.split(',')[1]
            else:
                base64_data = sketch_data
            # Декодируем base64 и создаем QPixmap
            image_data = base64.b64decode(base64_data)
            pixmap = QPixmap()
            if pixmap.loadFromData(image_data):
                # Масштабируем изображение
                scaled_pixmap = pixmap.scaled(200, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.ui.label_profile_sketch.setPixmap(scaled_pixmap)
                self.ui.label_profile_sketch.setText("")
                return
        # Если эскиз не найден, показываем заглушку
        self.ui.label_profile_sketch.clear()
        self.ui.label_profile_sketch.setText("Эскиз не найден")

    def get_selected_component(self):
        """Возвращает список выбранных компонентов"""
        list_selected_component = []
        for widget_data in self.list_component_widget:
            checkbox = widget_data['checkbox']
            if checkbox.isChecked():
                row = widget_data['row']
                # Получаем описание из таблицы
                description_item = self.ui.tableWidget_components.item(row, 3)
                description = description_item.text() if description_item else ""
                component = {
                    "type_id": widget_data['type_id'],
                    "variant": 1,
                    "description": description,
                    "status_id": 1
                }
                list_selected_component.append(component)
        return list_selected_component

    # =============================================================================
    # Создание инструмента профиля
    # =============================================================================
    @Slot()
    def create_profiletool(self):
        """Создает новый инструмент профиля"""
        dimension = self.ui.comboBox_dimension.currentData()
        description = self.ui.textEdit_description.toPlainText().strip()
        tool = {
            "profile_id": self.selected_profile['id'],
            "dimension_id": dimension['id'],
            "description": description
        }
         # Создаем инструмент
        result = api_manager.api_profiletool.create_profiletool(tool)
        profiletool_id = result['id']
        # Создаем выбранные компоненты
        for component in self.get_selected_component():
            api_manager.api_profiletool.create_profiletool_component(profiletool_id, component)

    def accept(self):
        """Принимает изменения и закрывает диалог"""
        self.create_profiletool()
        super().accept()