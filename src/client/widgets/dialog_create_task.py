"""Диалог создания задачи для инструмента."""

from datetime import date, timedelta
from typing import Dict, List, Optional

from PySide6.QtCore import QDate, QFile, Signal, Slot
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDateEdit,
    QDialog,
    QGroupBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

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
        
        if not ui_file.open(QFile.ReadOnly):
            raise FileNotFoundError(f"Не удалось открыть UI файл: {UI_PATHS['DIALOG_CREATE_TASK']}")
        
        loader = QUiLoader()
        self.ui = loader.load(ui_file, None)  # Загружаем без родителя
        ui_file.close()
        
        if self.ui is None:
            raise RuntimeError("Не удалось загрузить UI из файла")
        
        # Устанавливаем заголовок и свойства диалога
        self.setWindowTitle("Создание задачи для инструмента")
        self.setModal(True)
        
        # Установка layout для диалога
        layout = QVBoxLayout(self)
        layout.addWidget(self.ui)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
    
    def setup_ui(self) -> None:
        """Настройка элементов интерфейса."""
        # Подключение сигналов
        self.ui.comboBox_profile.currentTextChanged.connect(self.on_profile_changed)
        self.ui.comboBox_tool.currentTextChanged.connect(self.on_tool_changed)
        self.ui.pushButton_create.clicked.connect(self.create_task)
        
        # Подключаем кнопку отмены явно
        self.ui.pushButton_cancel.clicked.connect(self.reject)
        
        # Настройка даты по умолчанию (неделя от сегодня)
        default_date = date.today() + timedelta(days=7)
        self.ui.dateEdit_deadline.setDate(QDate.fromString(default_date.isoformat(), "yyyy-MM-dd"))
        
        # Минимальная дата - сегодня
        self.ui.dateEdit_deadline.setMinimumDate(QDate.currentDate())
        
        # Скрываем поле отдела для задач инструмента
        self.ui.label_department.setVisible(False)
        self.ui.comboBox_department.setVisible(False)
            

    
    def load_initial_data(self) -> None:
        """Загрузка начальных данных."""
        try:
            # Загружаем профили и инструменты
            self.array_profile_tool = self.api_client.get_profile_tool()
            # Заполняем комбобокс профилей
            self.populate_profile_combo()
            
        except Exception as e:
            print(f"Ошибка загрузки данных в диалоге: {e}")
            # Устанавливаем пустые значения при ошибке
            self.array_profile_tool = []
    
    def populate_profile_combo(self) -> None:
        """Заполнение комбобокса профилей."""
        self.ui.comboBox_profile.clear()
        
        # Добавляем placeholder, если нет данных
        if not self.array_profile_tool:
            self.ui.comboBox_profile.addItem("Нет доступных профилей", None)
            self.ui.comboBox_profile.setEnabled(False)
            return
        
        # Получаем уникальные профили
        dict_profile_used = {}
        for profile_tool in self.array_profile_tool:
            profile_id = profile_tool["profile_id"]
            if profile_id not in dict_profile_used:
                profile = references_manager.get_profile_by_id(profile_id)
                if profile:
                    dict_profile_used[profile_id] = profile
                    self.ui.comboBox_profile.addItem(
                        profile["article"], profile_id
                    )
    
    @Slot(str)
    def on_profile_changed(self, profile_article: str) -> None:
        """Обработка изменения профиля."""
        if not profile_article:
            self.ui.comboBox_tool.clear()
            self.ui.comboBox_tool.setEnabled(False)
            self.clear_components()
            return
        
        # Получаем ID выбранного профиля
        profile_id = self.ui.comboBox_profile.currentData()
        
        # Заполняем инструменты для данного профиля
        self.populate_tool_combo(profile_id)
        self.ui.comboBox_tool.setEnabled(True)
    
    def populate_tool_combo(self, profile_id: int) -> None:
        """Заполнение комбобокса инструментов для профиля."""
        self.ui.comboBox_tool.clear()
        
        # Фильтруем инструменты по профилю
        for profile_tool in self.array_profile_tool:
            if profile_tool["profile_id"] == profile_id:
                # Используем ID инструмента как название (можно потом улучшить)
                tool_name = f"Инструмент {profile_tool['dimension']}"
                self.ui.comboBox_tool.addItem(
                    tool_name, profile_tool["id"]
                )
    
    @Slot(str)
    def on_tool_changed(self, tool_name: str) -> None:
        """Обработка изменения инструмента."""
        if not tool_name:
            self.clear_components()
            self.ui.pushButton_create.setEnabled(False)
            return
        
        # Загружаем компоненты для выбранного инструмента
        self.load_tool_components()
    
    def load_tool_components(self) -> None:
        """Загрузка компонентов для выбранного инструмента."""
        profile_tool_id = self.ui.comboBox_tool.currentData()
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
        self.create_component_checkboxes(array_component_filtered)
    
    def create_component_checkboxes(self, array_component: List[Dict]) -> None:
        """Создание чекбоксов для компонентов."""
        self.clear_components()
        
        layout = self.ui.scrollAreaWidgetContents.layout()
        
        for component in array_component:
            checkbox = QCheckBox()
            
            # Получаем тип компонента как строку
            type_name = component.get("component_type", "Неизвестный тип")
            
            # Получаем статус как строку
            status_name = component.get("status", "Неизвестный статус")
            
            checkbox.setText(f"{type_name} ({status_name})")
            checkbox.stateChanged.connect(self.on_component_selection_changed)
            
            layout.addWidget(checkbox)
            self.dict_component_checkbox[component["id"]] = checkbox
        
        # Включаем кнопку создания, если есть компоненты
        self.update_create_button_state()
    
    def clear_components(self) -> None:
        """Очистка списка компонентов."""
        layout = self.ui.scrollAreaWidgetContents.layout()
        
        # Удаляем все чекбоксы
        for checkbox in self.dict_component_checkbox.values():
            layout.removeWidget(checkbox)
            checkbox.deleteLater()
        
        self.dict_component_checkbox.clear()
    
    @Slot()
    def on_component_selection_changed(self) -> None:
        """Обработка изменения выбора компонентов."""
        self.update_create_button_state()
    
    def update_create_button_state(self) -> None:
        """Обновление состояния кнопки создания."""
        # Проверяем, выбран ли хотя бы один компонент
        has_selected_components = any(
            cb.isChecked() for cb in self.dict_component_checkbox.values()
        )
        
        # Проверяем, заполнены ли обязательные поля
        has_tool = bool(self.ui.comboBox_tool.currentText())
        
        self.ui.pushButton_create.setEnabled(
            has_selected_components and has_tool
        )
    
    @Slot()
    def create_task(self) -> None:
        """Создание новой задачи."""
        # Собираем данные формы
        profile_tool_id = self.ui.comboBox_tool.currentData()
        deadline = self.ui.dateEdit_deadline.date().toString("yyyy-MM-dd")
        description = self.ui.textEdit_description.toPlainText().strip()
        
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
            "array_component_id": array_component_id  # Это для компонентов, отдельно от основной задачи
        }
        
        # Отправляем сигнал с данными
        self.task_created.emit(task_data)
        
        # Закрываем диалог
        self.accept()
    