"""Диалог для редактирования инструмента профиля."""
from PySide6.QtWidgets import (QDialog, QTableWidgetItem, QCheckBox, QAbstractItemView)
from PySide6.QtCore import QFile, Qt, Slot
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QPixmap
import base64
from ..constant import UI_PATHS_ABS
from ..api_manager import api_manager


class DialogEditProfileTool(QDialog):
    """Диалог для редактирования инструмента профиля с компонентами"""
    def __init__(self, profile_tool, parent=None):
        super().__init__(parent)
        self.profile_tool = profile_tool
        self.list_component_widget = []
        self.load_ui()
        self.setup_ui()
        # Заполняем форму данными инструмента
        self.fill_profile_tool()
        self.fill_component()

    def load_ui(self):
        """Загружает UI из файла"""
        ui_file = QFile(UI_PATHS_ABS["DIALOG_EDIT_PROFILE_TOOL"])
        ui_file.open(QFile.ReadOnly)
        loader = QUiLoader()
        self.ui = loader.load(ui_file)
        ui_file.close()

        # Устанавливаем заголовок и свойства диалога
        self.setWindowTitle("Редактирование инструмента профиля")
        self.setModal(True)
        self.setLayout(self.ui.layout())

    def setup_ui(self):
        """Настраивает UI компонентов после загрузки"""
        # Подключаем обработчики кнопок
        self.ui.buttonBox.accepted.connect(self.accept)
        self.ui.buttonBox.rejected.connect(self.reject)

        # Настройка таблицы компонентов
        self.ui.tableWidget_components.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ui.tableWidget_components.setSelectionMode(QAbstractItemView.SingleSelection)
        self.ui.tableWidget_components.horizontalHeader().setStretchLastSection(True)

        # Устанавливаем ширины колонок
        self.ui.tableWidget_components.setColumnWidth(0, 100)  # Использовать
        self.ui.tableWidget_components.setColumnWidth(1, 200)  # Тип компонента
        self.ui.tableWidget_components.setColumnWidth(2, 150)  # Статус

        self.setup_component_form()
    # =============================================================================
    # Загрузка справочников и начальных данных
    # =============================================================================
    def fill_profile_tool(self):
        """Заполняет форму данными редактируемого инструмента профиля."""
        # Заполняем основные поля
        profile = self.profile_tool['profile']
        profile_article = profile['article']
        dimension_name = self.profile_tool['dimension']['name']
        description = self.profile_tool['description']
        self.ui.label_profile.setText("профиль: " + profile_article)
        self.ui.label_dimension.setText("размерность: " + dimension_name)
        self.ui.textEdit_description.setPlainText(description)
        self.load_profile_sketch(profile)

    def fill_component(self):
        """Заполняет форму компонентами редактируемого инструмента профиля."""
        for component in self.profile_tool['component']:
            # Заполняем таблицу компонентами
            for widget_data in self.list_component_widget:
                type_id = widget_data['type_id']
                checkbox = widget_data['checkbox']
                row = widget_data['row']
                # Проверяем, есть ли компонент с этим типом
                if component['type_id'] == type_id:
                    checkbox.setChecked(True)
                    # Статус компонента
                    status_item = QTableWidgetItem(component['status']['name'])
                    status_item.setFlags(status_item.flags() & ~Qt.ItemIsEditable)
                    self.ui.tableWidget_components.setItem(row, 2, status_item)
                    # Описание компонента
                    description_item = QTableWidgetItem(component.get('description', ''))
                    self.ui.tableWidget_components.setItem(row, 3, description_item)

    def setup_component_form(self):
        """Загружает типы компонентов в таблицу"""
        # Очищаем таблицу
        self.ui.tableWidget_components.setRowCount(0)
        self.list_component_widget.clear()
        
        # Заполняем таблицу типами компонентов
        self.ui.tableWidget_components.setRowCount(len(api_manager.component_type))
        for row, type in enumerate(api_manager.component_type):
            # Колонка 0: Checkbox "Использовать"
            checkbox = QCheckBox()
            checkbox.setChecked(False)  # По умолчанию не выбран
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
                self.ui.label_sketch.setPixmap(scaled_pixmap)
                self.ui.label_sketch.setText("")
                return

        # Если эскиз не найден, показываем заглушку
        self.ui.label_sketch.clear()
        self.ui.label_sketch.setText("Эскиз не найден")

    # =============================================================================
    # Cбор данных
    # =============================================================================
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
                component_data = {
                    "type_id": widget_data['type_id'],
                    "variant": 1,  # Всегда первый вариант
                    "description": description,
                    "status_id": 1
                }
                list_selected_component.append(component_data)
        return list_selected_component

    # =============================================================================
    # Обновление инструмента профиля
    # =============================================================================
    @Slot()
    def update_profile_tool(self):
        """Обновляет существующий инструмент профиля"""
        description = self.ui.textEdit_description.toPlainText().strip()
        data = {
            "description": description
        }
        # Отправляем запрос на сервер для обновления инструмента
        api_manager.api_profile_tool.update_profile_tool(self.profile_tool['id'], data)

    def update_tool_component(self):
        """Обновляет компоненты инструмента"""
        if self.profile_tool['component']:
            api_manager.api_profile_tool.delete_profile_tool_component(self.profile_tool['id'])
        # Создаем новые выбранные компоненты
        for component_data in self.get_selected_component():
            api_manager.api_profile_tool.create_profile_tool_component(self.profile_tool['id'], component_data)

    def accept(self):
        """Принимает изменения и закрывает диалог"""
        self.update_profile_tool()
        self.update_tool_component()
        super().accept()
