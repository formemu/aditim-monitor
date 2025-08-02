"""Диалог создания задачи для инструмента."""

from datetime import date, timedelta
from typing import Dict, List, Optional

from PySide6.QtCore import QDate, QFile, Signal, Slot
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import (QCheckBox, QDialog, QVBoxLayout, QWidget, QSpinBox)

from ..api_client import ApiClient
from ..references_manager import references_manager


class DialogCreateTask(QDialog):
    """Диалог создания новой задачи для инструмента."""
    
    task_created = Signal(dict)
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self.ui: QWidget = None
        self.api_client = ApiClient()
        
        # Данные для работы
        self.array_profile_tool: List[Dict] = []
        self.dict_component_checkbox: Dict[int, QCheckBox] = {}

        # Данные для работы с изделиями
        self.array_product: List[Dict] = []
        self.dict_product_component_checkbox: Dict[int, QCheckBox] = {}
        self.dict_product_component_spinbox: Dict[int, QSpinBox] = {} 
        
        
        self.load_ui()
        self.setup_ui()
        
        # Загружаем данные, но не блокируем создание диалога при ошибках
        try:
            self.load_initial_data()
        except Exception as e:
            print(f"Ошибка загрузки данных в диалоге: {e}")
            # Диалог все равно должен показаться, даже если данные не загрузились
    
    def showEvent(self, event):
        """Обработчик события показа диалога."""
        # Устанавливаем явный размер
        self.resize(600, 500)
        self.setMinimumSize(600, 500)
        
        # Центрируем диалог относительно родителя
        if self.parent():
            parent_rect = self.parent().geometry()
            x = parent_rect.x() + (parent_rect.width() - self.width()) // 2
            y = parent_rect.y() + (parent_rect.height() - self.height()) // 2
            self.move(x, y)
        
        super().showEvent(event)
    
    def load_ui(self) -> None:
        """Загрузка UI из файла."""
        from ..constant import UI_PATHS_ABS as UI_PATHS
        ui_file = QFile(UI_PATHS["DIALOG_CREATE_TASK"])
                
        loader = QUiLoader()
        self.ui = loader.load(ui_file, None)  # Загружаем без родителя
        ui_file.close()
        
        if self.ui is None:
            raise RuntimeError("Не удалось загрузить UI из файла")
        
        # Устанавливаем заголовок и свойства диалога
        self.setWindowTitle("Создание задачи")
        self.setModal(True)
        
        # Установка layout для диалога
        layout = QVBoxLayout(self)
        layout.addWidget(self.ui)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
    
    def setup_ui(self) -> None:
        """Настройка элементов интерфейса."""
        # Подключение сигналов для инструментов
        self.ui.comboBox_profile_tool_profile.currentTextChanged.connect(self.on_profile_changed)
        self.ui.comboBox_profile_tool_tool.currentTextChanged.connect(self.on_tool_changed)
        
        # Подключение сигналов для изделий
        self.ui.comboBox_product.currentTextChanged.connect(self.on_product_changed)
        self.ui.comboBox_product_department.currentTextChanged.connect(self.on_department_changed)

        # Подключение сигналов для переключения вкладок
        self.ui.tabWidget.currentChanged.connect(self.on_tab_changed)

        # Общие кнопки
        self.ui.pushButton_create.clicked.connect(self.create_task)
        self.ui.pushButton_cancel.clicked.connect(self.reject)
        
        # Настройка даты по умолчанию (неделя от сегодня)
        default_date = date.today() + timedelta(days=7)
        self.ui.dateEdit_profile_tool_deadline.setDate(QDate.fromString(default_date.isoformat(), "yyyy-MM-dd"))
        self.ui.dateEdit_product_deadline.setDate(QDate.fromString(default_date.isoformat(), "yyyy-MM-dd"))
        
        # Минимальная дата - сегодня
        self.ui.dateEdit_profile_tool_deadline.setMinimumDate(QDate.currentDate())
        self.ui.dateEdit_product_deadline.setMinimumDate(QDate.currentDate())

    
    def load_initial_data(self) -> None:
        """Загрузка начальных данных."""
        try:
            # Загружаем профили и инструменты
            self.array_profile_tool = self.api_client.get_profile_tool()
            self.populate_profile_combo()
            
            # Загружаем изделия
            self.array_product = self.api_client.get_product()
            self.populate_product_combo()
            
            # Загружаем отделы для изделий
            self.populate_department_combo()
            
        except Exception as e:
            print(f"Ошибка загрузки данных в диалоге: {e}")
            # Устанавливаем пустые значения при ошибке
            self.array_profile_tool = []
            self.array_product = []
    
    def populate_profile_combo(self) -> None:
        """Заполнение комбобокса профилей."""
        self.ui.comboBox_profile_tool_profile.clear()
        
        # Добавляем placeholder, если нет данных
        if not self.array_profile_tool:
            self.ui.comboBox_profile_tool_profile.addItem("Нет доступных профилей", None)
            self.ui.comboBox_profile_tool_profile.setEnabled(False)
            return
        
        # Получаем уникальные профили
        dict_profile_used = {}
        for profile_tool in self.array_profile_tool:
            profile_id = profile_tool["profile_id"]
            if profile_id not in dict_profile_used:
                profile = references_manager.get_profile_by_id(profile_id)
                if profile:
                    dict_profile_used[profile_id] = profile
                    self.ui.comboBox_profile_tool_profile.addItem(
                        profile["article"], profile_id
                    )
    
    def populate_product_combo(self) -> None:
        """Заполнение комбобокса изделий."""
        self.ui.comboBox_product.clear()
        
        # Добавляем placeholder, если нет данных
        if not self.array_product:
            self.ui.comboBox_product.addItem("Нет доступных изделий", None)
            self.ui.comboBox_product.setEnabled(False)
            return
        
        # Заполняем изделиями
        for product in self.array_product:
            self.ui.comboBox_product.addItem(
                product["name"], product["id"]
            )

    def populate_department_combo(self) -> None:
        """Заполнение комбобокса отделов."""
        self.ui.comboBox_product_department.clear()
        
        # Получаем отделы из справочника
        dict_department = references_manager.get_department()
        
        if not dict_department:
            self.ui.comboBox_product_department.addItem("Нет доступных отделов", None)
            self.ui.comboBox_product_department.setEnabled(False)
            return
        
                # Заполняем отделами
        for dept_id, dept_name in dict_department.items():
            if dept_id > 0:  # Пропускаем пустое значение
                self.ui.comboBox_product_department.addItem(dept_name, dept_id)

    @Slot(str)
    def on_profile_changed(self, profile_article: str) -> None:
        """Обработка изменения профиля."""
        if not profile_article:
            self.ui.comboBox_profile_tool_tool.clear()
            self.ui.comboBox_profile_tool_tool.setEnabled(False)
            self.clear_profile_tool_component()
            return
        
        # Получаем ID выбранного профиля
        profile_id = self.ui.comboBox_profile_tool_profile.currentData()
        
        # Заполняем инструменты для данного профиля
        self.populate_tool_combo(profile_id)
        self.ui.comboBox_profile_tool_tool.setEnabled(True)
    
    def populate_tool_combo(self, profile_id: int) -> None:
        """Заполнение комбобокса инструментов для профиля."""
        self.ui.comboBox_profile_tool_tool.clear()

        # Фильтруем инструменты по профилю
        for profile_tool in self.array_profile_tool:
            if profile_tool["profile_id"] == profile_id:
                # Используем ID инструмента как название (можно потом улучшить)
                tool_name = f"Инструмент {profile_tool['dimension']}"
                self.ui.comboBox_profile_tool_tool.addItem(
                    tool_name, profile_tool["id"]
                )
    
    @Slot(str)
    def on_tool_changed(self, tool_name: str) -> None:
        """Обработка изменения инструмента."""
        if not tool_name:
            self.clear_profile_tool_component()
            self.ui.pushButton_create.setEnabled(False)
            return
        
        # Загружаем компоненты для выбранного инструмента
        self.load_tool_components()
    
    def load_tool_components(self) -> None:
        """Загрузка компонентов для выбранного инструмента."""
        profile_tool_id = self.ui.comboBox_profile_tool_tool.currentData()
        if not profile_tool_id:
            return
        
        # Получаем компоненты инструмента
        array_component = self.api_client.get_profile_tool_component(
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

    @Slot(str)
    def on_product_changed(self, product_name: str) -> None:
        """Обработка изменения изделия."""
        if not product_name:
            self.clear_product_component()
            self.update_create_button_state()
            return
        
        # Загружаем компоненты для выбранного изделия
        self.load_product_component()
        
    @Slot(str)
    def on_department_changed(self, department_name: str) -> None:
        """Обработка изменения отдела."""
        # Обновляем состояние кнопки при изменении отдела
        self.update_create_button_state()

    def load_product_component(self) -> None:
        """Загрузка компонентов для выбранного изделия."""
        product_id = self.ui.comboBox_product.currentData()
        if not product_id:
            return
        
        # Получаем компоненты изделия
        array_component = self.api_client.get_product_component(product_id)
        
        # Создаем чекбоксы для компонентов
        self.create_product_component_checkbox(array_component)

    def create_profile_tool_component_checkbox(self, array_component: List[Dict]) -> None:
        """Создание чекбоксов для компонентов."""
        self.clear_profile_tool_component()
        
        layout = self.ui.widget_profile_tool_content.layout()
        
        for component in array_component:
            checkbox = QCheckBox()
            
            # Получаем тип компонента как строку
            type_name = component.get("component_type", "Неизвестный тип")
            
            # Получаем статус как строку
            status_name = component.get("status", "Неизвестный статус")
            
            checkbox.setText(f"{type_name} ({status_name})")
            checkbox.stateChanged.connect(self.on_profile_tool_component_selection_changed)
            
            layout.addWidget(checkbox)
            self.dict_component_checkbox[component["id"]] = checkbox
        
        # Включаем кнопку создания, если есть компоненты
        self.update_create_button_state()

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
            component_name = component.get("component_name", "Неизвестный компонент")
            checkbox.setText(component_name)
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

    def clear_profile_tool_component(self) -> None:
        """Очистка списка компонентов."""
        layout = self.ui.widget_profile_tool_content.layout()
        
        # Удаляем все чекбоксы
        for checkbox in self.dict_component_checkbox.values():
            layout.removeWidget(checkbox)
            checkbox.deleteLater()
        
        self.dict_component_checkbox.clear()

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
    def on_profile_tool_component_selection_changed(self) -> None:
        """Обработка изменения выбора компонентов инструмента."""
        self.update_create_button_state()

    @Slot()
    def on_product_component_selection_changed(self) -> None:
        """Обработка изменения выбора компонентов изделия."""
        self.update_create_button_state()
    
    def update_create_button_state(self) -> None:
        """Обновление состояния кнопки создания."""
        current_tab = self.ui.tabWidget.currentIndex()
        
        if current_tab == 0:  # Вкладка инструментов
            # Проверяем ТОЛЬКО данные инструментов
            has_selected_components = any(
                cb.isChecked() for cb in self.dict_component_checkbox.values()
            )
            has_tool = bool(self.ui.comboBox_profile_tool_tool.currentText())
            
            # Кнопка активна только для инструментов
            self.ui.pushButton_create.setEnabled(
                has_selected_components and has_tool
            )
            
        elif current_tab == 1:  # Вкладка изделий
            # Проверяем ТОЛЬКО данные изделий
            has_selected_components = any(
                cb.isChecked() for cb in self.dict_product_component_checkbox.values()
            )
            has_product = bool(self.ui.comboBox_product.currentText())
            has_department = bool(self.ui.comboBox_product_department.currentText())
            
            print(has_selected_components and has_product and has_department)


            # Кнопка активна только для изделий
            self.ui.pushButton_create.setEnabled(
                has_selected_components and has_product and has_department
            )
        
        else:
            # Неизвестная вкладка
            self.ui.pushButton_create.setEnabled(False)
    
    @Slot(int)
    def on_tab_changed(self, index: int) -> None:
        """Обработка переключения вкладок."""
        # Обновляем состояние кнопки при переключении вкладок
        self.update_create_button_state()

    @Slot()
    def create_task(self) -> None:
        """Создание новой задачи."""
        current_tab = self.ui.tabWidget.currentIndex()
        
        if current_tab == 0:  # Создание задачи для инструмента
            self.create_profile_tool_task()
        elif current_tab == 1:  # Создание задачи для изделия
            self.create_product_task()

    def create_profile_tool_task(self) -> None:
        """Создание задачи для инструмента."""
        # Собираем данные формы
        profile_tool_id = self.ui.comboBox_profile_tool_tool.currentData()
        deadline = self.ui.dateEdit_profile_tool_deadline.date().toString("yyyy-MM-dd")
        description = self.ui.textEdit_profile_tool_description.toPlainText().strip()
        
        # Получаем выбранные компоненты
        array_component_id = [
            component_id for component_id, checkbox 
            in self.dict_component_checkbox.items()
            if checkbox.isChecked()
        ]
        
        # Создаем данные задачи для API
        task_data = {
            "profile_tool_id": profile_tool_id,
            "deadline_on": deadline,
            "department_id": 1,  # Временно используем ID=1, пока не добавим выбор отдела
            "stage": description if description else None,
            "array_component_id": array_component_id
        }
        
        # Отправляем сигнал с данными
        self.task_created.emit(task_data)
        
        # Закрываем диалог
        self.accept()

    def create_product_task(self) -> None:
        """Создание задачи для изделия."""
        # Собираем данные формы
        product_id = self.ui.comboBox_product.currentData()
        department_id = self.ui.comboBox_product_department.currentData()
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

        # Создаем данные задачи для API
        task_data = {
            "product_id": product_id,
            "department_id": department_id,
            "deadline_on": deadline,
            "stage": description if description else None,
            "array_component_data": array_component_data
        }
        
        # Отправляем сигнал с данными
        self.task_created.emit(task_data)
        
        # Закрываем диалог
        self.accept()