"""Диалог создания задачи для инструмента."""
from datetime import date, timedelta
from typing import Dict, List, Optional
from PySide6.QtCore import QDate, QFile, Slot, Qt
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QCheckBox, QDialog, QWidget, QListWidgetItem

from ..api_manager import api_manager
from ..constant import UI_PATHS_ABS

class DialogCreateTask(QDialog):
    """Диалог создания новой задачи для инструмента."""
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.profile = None
        self.profile_tool = None
        self.list_profile_tool_component = None
        self.product = None
        self.list_product_component = None
        self.load_ui()
        self.setup_ui()
   
    def load_ui(self) -> None:
        """Загрузка UI из файла."""
        ui_file = QFile(UI_PATHS_ABS["DIALOG_CREATE_TASK"])
        loader = QUiLoader()
        self.ui = loader.load(ui_file)
        ui_file.close()
        # Устанавливаем заголовок и свойства диалога
        self.setWindowTitle("Создание задачи")
        self.setModal(True)
        self.setLayout(self.ui.layout())
    
    def setup_ui(self) -> None:
        """Настройка элементов интерфейса."""
        # Подключение сигналов для инструментов
        self.ui.lineEdit_profile_search.textChanged.connect(self.on_profile_search_changed)
        self.ui.listWidget_profile_results.itemClicked.connect(self.on_profile_selected)
        self.ui.comboBox_profile_tool_tool.currentTextChanged.connect(self.on_tool_changed)
        # Подключение сигналов для изделий
        self.ui.comboBox_product.currentTextChanged.connect(self.on_product_changed)
        # Подключение сигналов для переключения вкладок
        self.ui.tabWidget.currentChanged.connect(self.update_create_button_state)
        # Общие кнопки
        self.ui.pushButton_create.clicked.connect(self.create_task)
        # Настройка даты по умолчанию (неделя от сегодня)
        default_date = date.today() + timedelta(days=7)
        self.ui.dateEdit_profile_tool_deadline.setDate(QDate.fromString(default_date.isoformat(), "yyyy-MM-dd"))
        self.ui.dateEdit_product_deadline.setDate(QDate.fromString(default_date.isoformat(), "yyyy-MM-dd"))
        # Минимальная дата - сегодня
        self.ui.dateEdit_profile_tool_deadline.setMinimumDate(QDate.currentDate())
        self.ui.dateEdit_product_deadline.setMinimumDate(QDate.currentDate())

    # =============================================================================
    # Управление вкладкой с инструментами профиля
    # =============================================================================
    @Slot(str)
    def on_profile_search_changed(self, text):
        """Обработчик изменения поискового запроса"""
        self.ui.listWidget_profile_results.clear()
        # Ищем профили через api_manager
        search_results = api_manager.get_search_profile(text)
        for profile in search_results[:10]:  # Показываем максимум 10 результатов
            display_text = f"{profile['article']} - {profile['description']}"
            item = QListWidgetItem(display_text)
            # Сохраняем данные профиля в элементе списка
            item.setData(Qt.UserRole, profile)
            self.ui.listWidget_profile_results.addItem(item)
    
    @Slot(QListWidgetItem)
    def on_profile_selected(self, item):
        """Обработчик выбора профиля из списка"""
        profile = item.data(Qt.UserRole)
        if profile:
            self.profile = profile
            # Обновляем поле поиска
            self.ui.lineEdit_profile_search.setText(profile['article'])
            # Скрываем список результатов
            self.ui.listWidget_profile_results.clear()
            self.fill_comboBox_profile_tool_tool()
        else:
            pass

    @Slot(str)
    def fill_comboBox_profile_tool_tool(self):
        """Обработка изменения профиля."""
        # Заполняем инструменты для данного профиля
        self.ui.comboBox_profile_tool_tool.clear()
        # Фильтруем инструменты по профилю
        for profile_tool in self.profile['profile_tool']:
            tool_name = f"Инструмент {profile_tool['dimension']}"
            self.ui.comboBox_profile_tool_tool.addItem(tool_name, profile_tool["id"] )
        self.ui.comboBox_profile_tool_tool.setEnabled(True)

    @Slot(str)
    def on_tool_changed(self, tool_name):
        """Обработка изменения инструмента."""
        if not tool_name:
            self.clear_profile_tool_component()
            self.ui.pushButton_create.setEnabled(False)
            return
        
        # Загружаем компоненты для выбранного инструмента
        self.load_tool_component()
    
    def load_tool_component(self) -> None:
        """Загрузка компонентов для выбранного инструмента."""
        profile_tool_id = self.ui.comboBox_profile_tool_tool.currentData()
        if not profile_tool_id:
            return
        # Получаем компоненты инструмента
        array_component = self.api_profile_tool.get_profile_tool_component(
            profile_tool_id
        )
        # Фильтруем только компоненты в разработке или изготовлении
        array_component_filtered = []
        for component in array_component:
            # Проверяем статус напрямую как строку
            status_value = component.get("status", "")
            if status_value in ["в разработке", "изготовление"]:
                array_component_filtered.append(component)
        # Создаем чекбоксы для компонентов
        self.create_profile_tool_component_checkbox(array_component_filtered)

    def create_profile_tool_component_checkbox(self, array_component: List[Dict]) -> None:
        """Создание чекбоксов для компонентов."""
        self.clear_profile_tool_component()
        
        layout = self.ui.widget_profile_tool_content.layout()
        
        for component in array_component:
            checkbox = QCheckBox()
            
            # Получаем тип компонента как строку
            type_name = component.get("component_type")
            
            # Получаем статус как строку
            status_name = component.get("status")
            
            checkbox.setText(f"{type_name} ({status_name})")
            checkbox.stateChanged.connect(self.on_profile_tool_component_selection_changed)
            
            layout.addWidget(checkbox)
            self.dict_profile_tool_component_checkbox[component["id"]] = checkbox
        
        # Включаем кнопку создания, если есть компоненты
        self.update_create_button_state()
 
    def clear_profile_tool_component(self) -> None:
        """Очистка списка компонентов."""
        layout = self.ui.widget_profile_tool_content.layout()
        
        # Удаляем все чекбоксы
        for checkbox in self.dict_profile_tool_component_checkbox.values():
            layout.removeWidget(checkbox)
            checkbox.deleteLater()
        
        self.dict_profile_tool_component_checkbox.clear()
    
    # =============================================================================
    # Управление вкладкой с изделиями
    # =============================================================================
    @Slot()
    def on_profile_tool_component_selection_changed(self) -> None:
        """Обработка изменения выбора компонентов инструмента."""
        self.update_create_button_state()

    @Slot(str)
    def on_product_changed(self, product_name: str) -> None:
        """Обработка изменения изделия."""
        if not product_name:
            self.clear_product_component()
            self.update_create_button_state()
            return
        
        # Загружаем компоненты для выбранного изделия
        self.load_product_component()
        
    def load_product_component(self) -> None:
        """Загрузка компонентов для выбранного изделия."""
        product_id = self.ui.comboBox_product.currentData()
        if not product_id:
            return
        
        # Получаем компоненты изделия
        array_component = self.api_product.get_product_component(product_id)
        
        # Создаем чекбоксы для компонентов
        self.create_product_component_checkbox(array_component)

    def create_product_component_checkbox(self, array_component: List[Dict]) -> None:
        """Создание чекбоксов для компонентов изделия."""
        self.clear_product_component()
        
        layout = self.ui.widget_product_content.layout()
        
        for component in array_component:
            # Создаем горизонтальный layout для чекбокса и спинбокса
            from PySide6.QtWidgets import QHBoxLayout, QWidget, QSpinBox
            
            container_widget = QWidget()
            horizontal_layout = QHBoxLayout(container_widget)
            horizontal_layout.setContentsMargins(0, 0, 0, 0)
            
            # Чекбокс
            checkbox = QCheckBox()
            name = component.get("name", "Неизвестный компонент")
            checkbox.setText(name)
            checkbox.stateChanged.connect(self.on_product_component_selection_changed)
            
            # SpinBox для количества
            spinbox = QSpinBox()
            spinbox.setMinimum(1)
            spinbox.setMaximum(999)
            spinbox.setValue(component.get("quantity", 1))  # Количество по умолчанию из API
            spinbox.setSuffix(" шт.")
            spinbox.setMinimumWidth(80)
            
            # Добавляем в горизонтальный layout
            horizontal_layout.addWidget(checkbox)
            horizontal_layout.addWidget(spinbox)
            horizontal_layout.addStretch()  # Растягиваем свободное пространство
            
            # Добавляем контейнер в основной layout
            layout.addWidget(container_widget)
            
            # Сохраняем ссылки
            self.dict_product_component_checkbox[component["id"]] = checkbox
            # Создаем новый словарь для спинбоксов изделий
            self.dict_product_component_spinbox[component["id"]] = spinbox
    
        # Обновляем состояние кнопки создания
        self.update_create_button_state()

    def clear_product_component(self) -> None:
        """Очистка списка компонентов изделия."""
        layout = self.ui.widget_product_content.layout()
        
        # Удаляем все чекбоксы
        for checkbox in self.dict_product_component_checkbox.values():
            layout.removeWidget(checkbox.parentWidget())
            checkbox.deleteLater()

        for spinbox in self.dict_product_component_spinbox.values():
            layout.removeWidget(checkbox.parentWidget())
            spinbox.deleteLater()

        self.dict_product_component_checkbox.clear()
        self.dict_product_component_spinbox.clear()
 
    @Slot()
    def on_product_component_selection_changed(self) -> None:
        """Обработка изменения выбора компонентов изделия."""
        self.update_create_button_state()
    
    # =============================================================================
    # Дополнительное поведение
    # =============================================================================
    def update_create_button_state(self) -> None:
        """Обновление состояния кнопки создания."""
        current_tab = self.ui.tabWidget.currentIndex()
        
        if current_tab == 0:  # Вкладка инструментов
            # Проверяем данные инструментов
            has_selected = any(cb.isChecked() for cb in self.dict_profile_tool_component_checkbox.values())
            has_tool = bool(self.ui.comboBox_profile_tool_tool.currentText())
            self.ui.pushButton_create.setEnabled(has_selected and has_tool)
            
        elif current_tab == 1:  # Вкладка изделий
            # Проверяем данные изделий
            has_selected = any(cb.isChecked() for cb in self.dict_product_component_checkbox.values())
            has_product = bool(self.ui.comboBox_product.currentText())
            self.ui.pushButton_create.setEnabled(has_selected and has_product)
    
    # =============================================================================
    # Создание задачи
    # =============================================================================
    @Slot()
    def create_task(self) -> None:
        """Создание новой задачи."""
        current_tab = self.ui.tabWidget.currentIndex()
        if current_tab == 0:  # Создание задачи для инструмента
            self.create_profile_tool_task()
        elif current_tab == 1:  # Создание задачи для изделия
            self.create_product_task()

    def create_profile_tool_task(self) -> None:
        """Создание задачи для инструмента с компонентами."""
        # Собираем данные формы
        profile_tool_id = self.ui.comboBox_profile_tool_tool.currentData()
        deadline = self.ui.dateEdit_profile_tool_deadline.date().toString("yyyy-MM-dd")
        description = self.ui.textEdit_profile_tool_description.toPlainText().strip()
        # Получаем выбранные компоненты
        array_component_id = []
        for component_id, checkbox in self.dict_profile_tool_component_checkbox.items():
            if checkbox.isChecked():
                array_component_id.append(component_id)
        # Создаем задачу через API
        task_data = {
            "profile_tool_id": profile_tool_id,
            "deadline_on": deadline,
            "description": description,
            "status_id": 1
        }
        response = self.api_task.create_task(task_data)
        task_id = response['id']
        if task_id:
            # Создаем компоненты задачи через API
            for component_id in array_component_id:
                comp_request = {
                    "task_id": task_id,
                    "profile_tool_component_id": component_id}
                self.api_task.create_task_component(comp_request)
        self.accept()

    def create_product_task(self):
        """Создание задачи для изделия с компонентами."""
        # Собираем данные формы
        product_id = self.ui.comboBox_product.currentData()
        deadline = self.ui.dateEdit_product_deadline.date().toString("yyyy-MM-dd")
        description = self.ui.textEdit_product_description.toPlainText().strip()
        # Получаем выбранные компоненты с количеством из SpinBox
        array_component_data = []
        for component_id, checkbox in self.dict_product_component_checkbox.items():
            if checkbox.isChecked():
                spinbox = self.dict_product_component_spinbox[component_id]
                array_component_data.append({
                    "product_component_id": component_id,
                    "quantity": spinbox.value()
                })
        # Создаем задачу через API
        task_data = {
            "product_id": product_id,
            "deadline_on": deadline,
            "description": description if description else None,
            "status_id": 1
        }
        response = self.api_task.create_task(task_data)
        task_id = response['id']
        if task_id:
            # Создаем компоненты задачи через API
            for comp_data in array_component_data:
                comp_request = {
                    "task_id": task_id,
                    "product_component_id": comp_data["product_component_id"],
                    "quantity": comp_data["quantity"] }
                self.api_task.create_task_component(comp_request)
        self.accept()
