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
        self.list_selected_profile_tool_component = []
        self.product = None
        self.list_selected_product_component = []
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
        # Подключаем обработчики кнопок
        self.ui.buttonBox.accepted.connect(self.accept)
        self.ui.buttonBox.rejected.connect(self.reject)
        # Подключение сигналов для инструментов
        self.ui.lineEdit_profile_search.textChanged.connect(self.on_profile_search_changed)
        self.ui.listWidget_profile_results.itemClicked.connect(self.on_profile_selected)
        self.ui.comboBox_profile_tool_tool.currentIndexChanged.connect(self.on_tool_changed)
        # Подключение сигналов для изделий
        self.ui.lineEdit_product_search.textChanged.connect(self.on_product_search_changed)
        self.ui.listWidget_product_results.itemClicked.connect(self.on_product_selected)
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
            tool_name = f"Инструмент {profile_tool['dimension']['name']}"
            self.ui.comboBox_profile_tool_tool.addItem(tool_name, profile_tool)
        self.ui.comboBox_profile_tool_tool.setEnabled(True)

    @Slot(str)
    def on_tool_changed(self, index):
        """Обработка изменения инструмента."""
        profile_tool = self.ui.comboBox_profile_tool_tool.itemData(index)
        self.profile_tool = profile_tool
        # Загружаем компоненты для выбранного инструмента
        self.load_tool_component()
    
    def load_tool_component(self):
        """Загрузка компонентов для выбранного инструмента."""
        # Фильтруем только компоненты в разработке или изготовлении
        list_component_filtered = []
        for component in self.profile_tool['component']:
            status = component['status']['name']
            if status in ["в разработке", "изготовление"]:
                list_component_filtered.append(component)
        # Создаем чекбоксы для компонентов
        self.create_profile_tool_component_checkbox(list_component_filtered)

    def create_profile_tool_component_checkbox(self, list_component):
        """Создание чекбоксов для компонентов."""
        self.clear_profile_tool_component()
        layout = self.ui.widget_profile_tool_content.layout()
        for component in list_component:
            checkbox = QCheckBox()
            type_name = component["type"]["name"]
            status_name = component["status"]["name"]
            checkbox.setText(f"{type_name} ({status_name})")
            checkbox.setProperty("profile_tool_component", component)
            layout.addWidget(checkbox)

    def clear_profile_tool_component(self):
        """Очистка списка компонентов."""
        self.list_selected_profile_tool_component.clear()
        layout = self.ui.widget_profile_tool_content.layout()
        if layout is not None:
            for i in reversed(range(layout.count())):
                widget = layout.itemAt(i).widget()
                if widget is not None:
                    widget.deleteLater()

    def get_selected_profile_tool_component(self):
        """Возвращает данные из отмеченного чекбокса."""
        layout = self.ui.widget_profile_tool_content.layout()
        for i in range(layout.count()):
            widget = layout.itemAt(i).widget()
            if isinstance(widget, QCheckBox) and widget.isChecked():
                component_data = widget.property("profile_tool_component")
                self.list_selected_profile_tool_component.append(component_data)

    # =============================================================================
    # Управление вкладкой с изделиями
    # =============================================================================
    @Slot(str)
    def on_product_search_changed(self, text):
        """Обработчик изменения поискового запроса"""
        self.ui.listWidget_product_results.clear()
        # Ищем изделия через api_manager
        search_results = api_manager.get_search_product(text)
        for product in search_results[:10]:  # Показываем максимум 10 результатов
            display_text = f"{product['name']} - {product['description']}"
            item = QListWidgetItem(display_text)
            # Сохраняем данные изделия в элементе списка
            item.setData(Qt.UserRole, product)
            self.ui.listWidget_product_results.addItem(item)

    @Slot(QListWidgetItem)
    def on_product_selected(self, item):
        """Обработчик выбора изделия из списка"""
        product = item.data(Qt.UserRole)
        if product:
            self.product = product
            # Обновляем поле поиска
            self.ui.lineEdit_product_search.setText(product['name'])
            # Скрываем список результатов
            self.ui.listWidget_product_results.clear()
            self.load_product_component()
        else:
            pass
            
    def load_product_component(self):
        """Загрузка компонентов для выбранного изделия."""
        # Фильтруем только компоненты в разработке или изготовлении
        list_component_filtered = []
        for component in self.product['component']:
            # TODO подумать можно ли совмещать статус копонентов для инструментов и продуктов или сделать отдельно
            # TODO статус для компонетов продуктов
            list_component_filtered.append(component)
        # Создаем чекбоксы для компонентов
        self.create_product_component_checkbox(list_component_filtered)

    def create_product_component_checkbox(self, list_component):
        """Создание чекбоксов для компонентов."""
        self.clear_product_component()
        layout = self.ui.widget_product_content.layout()
        for component in list_component:
            checkbox = QCheckBox()
            name = component["name"]
            checkbox.setText(f"{name}")
            checkbox.setProperty("product_component", component)
            layout.addWidget(checkbox)

    def clear_product_component(self):
        """Очистка списка компонентов."""
        layout = self.ui.widget_product_content.layout()
        if layout is not None:
            for i in reversed(range(layout.count())):
                widget = layout.itemAt(i).widget()
                if widget is not None:
                    widget.deleteLater()

    def get_selected_product_component(self):
        """Возвращает данные из отмеченного чекбокса."""
        layout = self.ui.widget_product_content.layout()
        for i in range(layout.count()):
            widget = layout.itemAt(i).widget()
            if isinstance(widget, QCheckBox) and widget.isChecked():
                component_data = widget.property("product_component")
                self.list_selected_product_component.append(component_data)

    # =============================================================================
    # Создание задачи
    # =============================================================================
    def create_profile_tool_task(self):
        """Создание задачи для инструмента с компонентами."""
        # Собираем данные формы
        deadline = self.ui.dateEdit_profile_tool_deadline.date().toString("yyyy-MM-dd")
        created = QDate.currentDate().toString("yyyy-MM-dd")
        description = self.ui.textEdit_profile_tool_description.toPlainText().strip()
        # Получаем выбранные компоненты
        self.get_selected_profile_tool_component()
        # Создаем задачу через API
        task_data = {
            "profile_tool_id": self.profile_tool['id'],
            "deadline": deadline,
            "created": created,
            "description": description,
            "status_id": 1
        }
        task = api_manager.api_task.create_task(task_data)
        task_id = task['id']
        # Добавляем компоненты
        for component_data in self.list_selected_profile_tool_component:
            # Подготавливаем данные компонента
            component_payload = {
                "profile_tool_component_id": component_data['id'],
                "description": ""
            }
            # Передаём task_id как отдельный аргумент
            api_manager.api_task.create_task_component(task_id, component_payload)
 

    def create_product_task(self):
        """Создание задачи для изделия с компонентами."""
        # Собираем данные формы
        deadline = self.ui.dateEdit_product_deadline.date().toString("yyyy-MM-dd")
        created = QDate.currentDate().toString("yyyy-MM-dd")
        description = self.ui.textEdit_product_description.toPlainText().strip()
        self.get_selected_product_component()
        # Создаем задачу через API
        task_data = {
            "product_id": self.product['id'],
            "deadline": deadline,
            "description": description,
            "status_id": 1,
            "created": created
        }
        task = api_manager.api_task.create_task(task_data)
        task_id = task['id']

        for component_data in self.list_selected_product_component:
            component = {
                "product_component_id": component_data['id'],
                "description": ''
            }
            api_manager.api_task.create_task_component(task_id, component)

    def accept(self):
        """Принять изменения и закрыть диалог."""
        current_tab = self.ui.tabWidget.currentIndex()
        if current_tab == 0:  # Создание задачи для инструмента
            self.create_profile_tool_task()
        elif current_tab == 1:  # Создание задачи для изделия
            self.create_product_task()
        super().accept()
