"""ПЕРЕРАБОТАТЬ load_dimensions_for_profile"""

"""
Диалог для создания инструмента профиля
"""

from typing import Dict, Any, Optional, List
from PySide6.QtWidgets import (QDialog, QMessageBox, QTableWidgetItem, 
                               QCheckBox, QComboBox, QAbstractItemView, QListWidgetItem)
from PySide6.QtCore import Signal, QFile, Qt
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QPixmap
import base64

from ..constant import UI_PATHS_ABS as UI_PATHS
from ..api_client import ApiClient
from ..references_manager import references_manager
from ..style_util import load_styles_with_constants


class DialogCreateProfileTool(QDialog):
    """Диалог для создания инструмента профиля с компонентами"""
    
    profile_tool_created = Signal(dict)  # Сигнал об успешном создании инструмента

    def __init__(self, api_client: ApiClient, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.selected_profile = None  # Выбранный профиль
        self.component_widgets = []   # Список виджетов компонентов (checkbox, combobox)
        
        # Загружаем UI файл
        self.load_ui()
       
        # Настраиваем логику
        self.setup_ui()
        self.load_component_types()

    def load_ui(self):
        """Загружает UI из файла"""
        ui_file = QFile(UI_PATHS["DIALOG_CREATE_PROFILE_TOOL"])
        ui_file.open(QFile.ReadOnly)
        
        loader = QUiLoader()
        self.ui = loader.load(ui_file)
        ui_file.close()

        # Устанавливаем свойства диалога
        self.setWindowTitle(self.ui.windowTitle())
        self.setModal(True)
        self.resize(self.ui.size())
        
        # Заменяем layout диалога на layout из UI файла
        if self.ui.layout():
            self.setLayout(self.ui.layout())

    def setup_ui(self):
        """Настраивает UI компонентов после загрузки"""
        # Подключаем обработчики кнопок
        self.ui.buttonBox.accepted.connect(self.create_profile_tool)
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
        
        # Предзагружаем размерности (общие для всех профилей)
        self.load_default_dimensions()
        
        # Фокус на поле поиска профиля
        self.ui.lineEdit_profile_search.setFocus()

    def load_default_dimensions(self):
        """Загружает размерности по умолчанию"""
        try:
            # Загружаем размерности инструментов из справочника
            tool_dimensions = references_manager.load_tool_dimensions()
            
            self.ui.comboBox_dimension.clear()
            if tool_dimensions:
                # Используем правильное поле - 'dimension' из API ответа
                dimensions = [dim.get('dimension', dim.get('name', '')) for dim in tool_dimensions]
                self.ui.comboBox_dimension.addItems(dimensions)
            else:
                # Если справочник пуст, используем захардкоженные значения
                self.ui.comboBox_dimension.addItems(['40x20', '50x30', '60x40', '25x15'])
                
        except Exception as e:
            # Добавляем значения по умолчанию
            self.ui.comboBox_dimension.clear()
            self.ui.comboBox_dimension.addItems(['40x20', '50x30', '60x40', '25x15'])

    def on_profile_search_changed(self, text: str):
        """Обработчик изменения поискового запроса"""
        self.ui.listWidget_profile_results.clear()
        
        if len(text) < 2:  # Начинаем поиск с 2 символов
            return
        
        # Ищем профили через references_manager
        search_results = references_manager.search_profiles(text)
        
        for profile in search_results[:10]:  # Показываем максимум 10 результатов
            display_text = f"{profile['article']} - {profile.get('description', '')}"
            item = QListWidgetItem(display_text)
            # Сохраняем данные профиля в элементе списка
            item.setData(Qt.UserRole, profile)
            self.ui.listWidget_profile_results.addItem(item)
        

    def on_profile_selected(self, item):
        """Обработчик выбора профиля из списка"""
        profile_data = item.data(Qt.UserRole)
        if profile_data:
            self.selected_profile = profile_data
            
            # Обновляем поле поиска
            self.ui.lineEdit_profile_search.setText(profile_data['article'])
            
            # Скрываем список результатов
            self.ui.listWidget_profile_results.clear()
            
            # Загружаем размерности для профиля
            self.load_dimensions_for_profile(profile_data['id'])
            
            # Загружаем эскиз профиля
            self.load_profile_sketch(profile_data['id'])
        else:
            pass

    def load_dimensions_for_profile(self, profile_id: int):
        """Загружает размерности для выбранного профиля"""
        try:
            # Пробуем загрузить специфичные для профиля размерности
            dimensions = references_manager.load_profile_dimensions(profile_id)
            
            if not dimensions:
                # Если нет специфичных размерностей, используем общие из tool-dimensions
                tool_dimensions = references_manager.load_tool_dimensions()
                dimensions = [dim.get('dimension', dim.get('name', '')) for dim in tool_dimensions]
            
            self.ui.comboBox_dimension.clear()
            if dimensions:
                self.ui.comboBox_dimension.addItems(dimensions)
            else:
                # Последняя попытка - значения по умолчанию
                self.ui.comboBox_dimension.addItems(['40x20', '50x30', '60x40', '25x15'])
            
        except Exception as e:
            # Добавляем значения по умолчанию
            self.ui.comboBox_dimension.clear()
            self.ui.comboBox_dimension.addItems(['40x20', '50x30', '60x40', '25x15'])

    def load_profile_sketch(self, profile_id: int):
        """Загружает и отображает эскиз профиля"""
        try:
            # Получаем данные профиля из references_manager
            profile = references_manager.get_profile(profile_id)
            
            if profile and profile.get('sketch'):
                # Конвертируем base64 в QPixmap
                sketch_data = profile['sketch']
                if sketch_data.startswith('data:image'):
                    # Убираем префикс data:image/...;base64,
                    base64_data = sketch_data.split(',')[1]
                else:
                    base64_data = sketch_data
                
                image_data = base64.b64decode(base64_data)
                pixmap = QPixmap()
                result = pixmap.loadFromData(image_data)
                
                if not pixmap.isNull():
                    # Масштабируем изображение под размер label
                    scaled_pixmap = pixmap.scaled(
                        200, 150, 
                        Qt.KeepAspectRatio, 
                        Qt.SmoothTransformation
                    )
                    self.ui.label_profile_sketch.setPixmap(scaled_pixmap)
                    self.ui.label_profile_sketch.setText("")
                else:
                    self.ui.label_profile_sketch.setText("Ошибка загрузки эскиза")
            else:
                self.ui.label_profile_sketch.setText("Эскиз не найден")
                
        except Exception as e:
            self.ui.label_profile_sketch.setText("Ошибка загрузки эскиза")

    def load_component_types(self):
        """Загружает типы компонентов в таблицу"""
        try:
            component_types = references_manager.get_component_types()
            statuses = references_manager.get_statuses()
            default_status_id = references_manager.get_default_status_id()
            
            # Очищаем таблицу
            self.ui.tableWidget_components.setRowCount(0)
            self.component_widgets.clear()
            
            # Заполняем таблицу типами компонентов
            self.ui.tableWidget_components.setRowCount(len(component_types))
            
            for row, (type_id, type_data) in enumerate(component_types.items()):
                # Колонка 0: Checkbox "Использовать"
                checkbox = QCheckBox()
                checkbox.setChecked(False)  # По умолчанию не выбран
                self.ui.tableWidget_components.setCellWidget(row, 0, checkbox)
                
                # Колонка 1: Название типа компонента
                name_item = QTableWidgetItem(type_data['name'])
                name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
                name_item.setData(Qt.UserRole, type_id)  # Сохраняем ID типа
                self.ui.tableWidget_components.setItem(row, 1, name_item)
                
                # Колонка 2: ComboBox статусов
                status_combo = QComboBox()
                for status_id, status_name in statuses.items():
                    status_combo.addItem(status_name, status_id)
                # Устанавливаем статус по умолчанию
                status_index = status_combo.findData(default_status_id)
                if status_index >= 0:
                    status_combo.setCurrentIndex(status_index)
                self.ui.tableWidget_components.setCellWidget(row, 2, status_combo)
                
                # Колонка 3: Описание
                description_item = QTableWidgetItem(type_data.get('description', ''))
                description_item.setFlags(description_item.flags() | Qt.ItemIsEditable)
                self.ui.tableWidget_components.setItem(row, 3, description_item)
                
                # Сохраняем ссылки на виджеты для удобного доступа
                self.component_widgets.append({
                    'type_id': type_id,
                    'checkbox': checkbox,
                    'status_combo': status_combo,
                    'row': row
                })
                
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить типы компонентов: {e}")

    def create_profile_tool(self):
        """Создает новый инструмент профиля"""
        try:
            # Валидация данных
            tool_data = self.validate_and_get_data()
            
            # Отправляем запрос на сервер для создания инструмента
            result = self.api_client.create_profile_tool(tool_data)
            tool_id = result.get('id')
            
            if not tool_id:
                raise ValueError("Сервер не вернул ID созданного инструмента")
            
            # Создаем выбранные компоненты
            selected_components = self.get_selected_components()
            for component_data in selected_components:
                try:
                    self.api_client.create_profile_tool_component(tool_id, component_data)
                except Exception as comp_error:
                    # Продолжаем создание остальных компонентов
                    pass
            
            # Уведомляем об успехе
            QMessageBox.information(
                self, 
                "Успех", 
                f"Инструмент профиля успешно создан!\nПрофиль: {self.selected_profile['article']}\nРазмерность: {tool_data.get('dimension', '')}"
            )
            
            # Испускаем сигнал о создании инструмента
            self.profile_tool_created.emit(result)
            
            # Закрываем диалог
            self.accept()
            
        except ValueError as e:
            QMessageBox.warning(self, "Ошибка валидации", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось создать инструмент профиля: {e}")

    def validate_and_get_data(self) -> Dict[str, Any]:
        """Валидирует введенные данные и возвращает их"""
        if not self.selected_profile:
            raise ValueError("Необходимо выбрать профиль")
        
        dimension = self.ui.comboBox_dimension.currentText().strip()
        if not dimension:
            raise ValueError("Необходимо выбрать размерность")
        
        description = self.ui.textEdit_description.toPlainText().strip()
        
        # Проверяем что выбран хотя бы один компонент
        selected_components = self.get_selected_components()
        if not selected_components:
            raise ValueError("Необходимо выбрать хотя бы один компонент")
        
        data = {
            "profile_id": self.selected_profile['id'],
            "dimension": dimension,
            "description": description if description else None,
            "profile_article": self.selected_profile['article']  # Для отображения
        }
        
        return data

    def get_selected_components(self) -> List[Dict[str, Any]]:
        """Возвращает список выбранных компонентов"""
        selected_components = []
        
        for widget_data in self.component_widgets:
            checkbox = widget_data['checkbox']
            if checkbox.isChecked():
                status_combo = widget_data['status_combo']
                row = widget_data['row']
                
                # Получаем описание из таблицы
                description_item = self.ui.tableWidget_components.item(row, 3)
                description = description_item.text() if description_item else ""
                
                component_data = {
                    "component_type_id": widget_data['type_id'],
                    "status_id": status_combo.currentData(),
                    "variant": 1,  # Всегда первый вариант
                    "description": description
                }
                selected_components.append(component_data)
        
        return selected_components

    def get_tool_data(self) -> Optional[Dict[str, Any]]:
        """Возвращает данные инструмента без валидации (для предварительного просмотра)"""
        try:
            return self.validate_and_get_data()
        except ValueError:
            return None
