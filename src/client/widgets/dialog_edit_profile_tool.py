"""
Диалог для редактирования существующего инструмента профиля.
"""

from typing import Dict, Any, Optional, List
from PySide6.QtWidgets import (QDialog, QMessageBox, QTableWidgetItem, 
                               QCheckBox, QComboBox, QAbstractItemView, QListWidgetItem)
from PySide6.QtCore import Signal, QFile, Qt, Slot
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QPixmap
import base64

from ..constant import UI_PATHS_ABS as UI_PATHS
from ..api.api_profile_tool import ApiProfileTool
from ..references_manager import references_manager
from ..style_util import load_styles


class DialogEditProfileTool(QDialog):
    """Диалог для редактирования инструмента профиля с компонентами"""
    profile_tool_updated = Signal(dict)  # Сигнал об успешном обновлении инструмента

    def __init__(self, profile_tool_data: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.api_profile_tool = ApiProfileTool()
        self.profile_tool_data = profile_tool_data
        self.profile_tool_id = profile_tool_data.get('id')
        self.component_widgets = []   # Список виджетов компонентов (checkbox, combobox)
        self.selected_profile = None
        self.existing_components = []  # Список существующих компонентов

        self.load_ui()
        self.setup_ui()
        self.load_component_type()
        self.load_default_dimension()
        
        # Заполняем форму данными инструмента
        self.fill_form_with_tool_data()

    def load_ui(self):
        """Загружает UI из файла"""
        ui_file = QFile(UI_PATHS["DIALOG_EDIT_PROFILE_TOOL"])
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
        self.ui.buttonBox.accepted.connect(self.update_profile_tool)
        self.ui.buttonBox.rejected.connect(self.reject)

        # Подключаем поиск профилей
        self.ui.lineEdit_profile_search.textChanged.connect(self.on_profile_search_changed)
        self.ui.listWidget_profile_results.itemClicked.connect(self.on_profile_selected)

        # Настройка таблицы компонентов
        self.ui.tableWidget_components.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ui.tableWidget_components.setSelectionMode(QAbstractItemView.SingleSelection)
        self.ui.tableWidget_components.horizontalHeader().setStretchLastSection(True)

        # Устанавливаем ширины колонок
        self.ui.tableWidget_components.setColumnWidth(0, 100)  # Использовать
        self.ui.tableWidget_components.setColumnWidth(1, 200)  # Тип компонента
        self.ui.tableWidget_components.setColumnWidth(2, 150)  # Статус

    def fill_form_with_tool_data(self):
        """Заполняет форму данными редактируемого инструмента профиля."""
        # Заполняем основные поля
        dimension = self.profile_tool_data.get('dimension', '')
        description = self.profile_tool_data.get('description', '')
        
        self.ui.textEdit_description.setPlainText(description)
        
        # Устанавливаем размерность
        dimension_index = self.ui.comboBox_dimension.findText(dimension)
        if dimension_index >= 0:
            self.ui.comboBox_dimension.setCurrentIndex(dimension_index)

        # Загружаем информацию о профиле
        profile_id = self.profile_tool_data.get('profile_id')
        if profile_id:
            self.load_profile_info(profile_id)

        # Загружаем существующие компоненты
        self.load_existing_components()

    def load_profile_info(self, profile_id: int):
        """Загружает информацию о профиле инструмента."""
        try:
            profile = references_manager.get_profile().get(profile_id)
            if profile:
                self.selected_profile = profile
                article = profile.get('article', '')
                self.ui.lineEdit_profile_search.setText(article)
                
                # Загружаем эскиз профиля
                self.load_profile_sketch(profile_id)
        except Exception as e:
            print(f"Ошибка загрузки информации о профиле: {e}")

    def load_existing_components(self):
        """Загружает существующие компоненты инструмента."""
        try:
            self.existing_components = self.api_profile_tool.get_profile_tool_component(self.profile_tool_id)
        except Exception as e:
            print(f"Ошибка загрузки компонентов: {e}")
            self.existing_components = []

    # =============================================================================
    # Загрузка справочников и начальных данных
    # =============================================================================
    def load_default_dimension(self):
        """Загружает размерности по умолчанию"""
        # Загружаем размерности инструментов из справочника
        dimension_dict = references_manager.get_dimension()
        self.ui.comboBox_dimension.clear()

        # Извлекаем значения dimension из словаря
        dimension_list = []
        for dimension in dimension_dict.values():
            dimension_list.append(dimension.get('dimension'))
        self.ui.comboBox_dimension.addItems(dimension_list)

    def load_component_type(self):
        """Загружает типы компонентов в таблицу"""
        component_type = references_manager.get_component_type()
        # Очищаем таблицу
        self.ui.tableWidget_components.setRowCount(0)
        self.component_widgets.clear()

        # Заполняем таблицу типами компонентов
        self.ui.tableWidget_components.setRowCount(len(component_type))
        for row, (type_id, type_data) in enumerate(component_type.items()):
            # Колонка 0: Checkbox "Использовать"
            checkbox = QCheckBox()
            
            # Проверяем, используется ли этот тип компонента уже
            is_used = any(comp.get('component_type_id') == type_id for comp in self.existing_components)
            checkbox.setChecked(is_used)
            
            self.ui.tableWidget_components.setCellWidget(row, 0, checkbox)

            # Колонка 1: Название типа компонента
            name_item = QTableWidgetItem(type_data['name'])
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
            name_item.setData(Qt.UserRole, type_id)  # Сохраняем ID типа
            self.ui.tableWidget_components.setItem(row, 1, name_item)

            # Колонка 2: Статус (пустой для редактирования)
            status_item = QTableWidgetItem("")
            self.ui.tableWidget_components.setItem(row, 2, status_item)

            # Колонка 3: Описание (находим из существующих компонентов)
            existing_comp = next((comp for comp in self.existing_components if comp.get('component_type_id') == type_id), None)
            description = existing_comp.get('description', '') if existing_comp else ""
            description_item = QTableWidgetItem(description)
            self.ui.tableWidget_components.setItem(row, 3, description_item)

            # Сохраняем ссылки на виджеты для удобного доступа
            self.component_widgets.append({
                'type_id': type_id,
                'checkbox': checkbox,
                'row': row
            })

    # =============================================================================
    # Управление поиском и выбором профиля
    # =============================================================================
    @Slot(str)
    def on_profile_search_changed(self, text: str):
        """Обработчик изменения поискового запроса"""
        self.ui.listWidget_profile_results.clear()
        if len(text) < 2:  # Начинаем поиск с 2 символов
            return

        # Ищем профили через references_manager
        search_results = references_manager.search_profile(text)
        for profile in search_results[:10]:  # Показываем максимум 10 результатов
            display_text = f"{profile['article']} - {profile.get('description', '')}"
            item = QListWidgetItem(display_text)
            # Сохраняем данные профиля в элементе списка
            item.setData(Qt.UserRole, profile)
            self.ui.listWidget_profile_results.addItem(item)

    @Slot(QListWidgetItem)
    def on_profile_selected(self, item):
        """Обработчик выбора профиля из списка"""
        profile_data = item.data(Qt.UserRole)
        if profile_data:
            self.selected_profile = profile_data
            # Обновляем поле поиска
            self.ui.lineEdit_profile_search.setText(profile_data['article'])
            # Скрываем список результатов
            self.ui.listWidget_profile_results.clear()
            # Загружаем эскиз профиля
            self.load_profile_sketch(profile_data['id'])

    def load_profile_sketch(self, profile_id: int):
        """Загружает и отображает эскиз профиля"""
        try:
            # Получаем данные профиля из references_manager
            profile = references_manager.get_profile().get(profile_id)
            if profile and profile.get('sketch'):
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

        except Exception as e:
            print(f"Ошибка загрузки эскиза: {e}")
            self.ui.label_sketch.clear()
            self.ui.label_sketch.setText("Ошибка загрузки эскиза")

    # =============================================================================
    # Валидация и сбор данных
    # =============================================================================
    def validate_and_get_data(self) -> Dict[str, Any]:
        """Валидирует данные формы и возвращает словарь для отправки на сервер"""
        if not self.selected_profile:
            raise ValueError("Необходимо выбрать профиль")

        dimension = self.ui.comboBox_dimension.currentText()
        if not dimension:
            raise ValueError("Необходимо выбрать размерность")

        description = self.ui.textEdit_description.toPlainText().strip()

        return {
            "profile_id": self.selected_profile['id'],
            "dimension": dimension,
            "description": description if description else None
        }

    def get_selected_components(self) -> List[Dict[str, Any]]:
        """Возвращает список выбранных компонентов"""
        selected_components = []
        for widget_data in self.component_widgets:
            checkbox = widget_data['checkbox']
            if checkbox.isChecked():
                row = widget_data['row']
                # Получаем описание из таблицы
                description_item = self.ui.tableWidget_components.item(row, 3)
                description = description_item.text() if description_item else ""
                component_data = {
                    "component_type_id": widget_data['type_id'],
                    "variant": 1,  # Всегда первый вариант
                    "description": description
                }
                selected_components.append(component_data)
        return selected_components

    # =============================================================================
    # Обновление инструмента профиля
    # =============================================================================
    @Slot()
    def update_profile_tool(self):
        """Обновляет существующий инструмент профиля"""
        try:
            # Валидация данных
            tool_data = self.validate_and_get_data()

            # Отправляем запрос на сервер для обновления инструмента
            updated_tool = self.api_profile_tool.update_profile_tool(self.profile_tool_id, tool_data)

            # Обновляем компоненты
            self.update_tool_components()

            # Уведомляем об успешном обновлении
            self.profile_tool_updated.emit(updated_tool)
            
            QMessageBox.information(
                self,
                "Успех",
                "Инструмент профиля успешно обновлён!"
            )
            self.accept()

        except ValueError as e:
            QMessageBox.warning(self, "Ошибка валидации", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка при обновлении инструмента профиля:\n{e}")

    def update_tool_components(self):
        """Обновляет компоненты инструмента"""
        try:
            # Удаляем все существующие компоненты
            for existing_comp in self.existing_components:
                try:
                    self.api_profile_tool.delete_profile_tool_component_by_id(existing_comp['id'])
                except Exception as e:
                    print(f"Ошибка удаления компонента {existing_comp['id']}: {e}")

            # Создаем новые выбранные компоненты
            selected_components = self.get_selected_components()
            for component_data in selected_components:
                try:
                    self.api_profile_tool.create_profile_tool_component(self.profile_tool_id, component_data)
                except Exception as comp_error:
                    print(f"Ошибка создания компонента: {comp_error}")

        except Exception as e:
            print(f"Ошибка обновления компонентов: {e}")
            # Не прерываем процесс, компоненты - дополнительная функциональность
