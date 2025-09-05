from datetime import date
from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import (QWizard, QWizardPage, QVBoxLayout, QLabel,
                               QLineEdit, QListWidget, QListWidgetItem, QCheckBox,
                               QComboBox, QDateEdit, QTextEdit, QGroupBox)
from PySide6.QtGui import QIntValidator

from ..api_manager import api_manager


class WizardTaskCreate(QWizard):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Создание задачи")
        self.setWizardStyle(QWizard.ModernStyle)
        self.setMinimumSize(700, 500)

        # Общие данные
        self.profile = None
        self.profile_tool = None
        self.product = None
        self.list_selected_profile_tool_component = []
        self.list_selected_product_component = []

        # Добавляем страницы
        self.addPage(PageStart(self))
        self.addPage(PageProfileSelection(self))
        self.addPage(PageToolSelection(self))
        self.addPage(PageComponentSelection(self))
        self.addPage(PageProductSelection(self))
        self.addPage(PageProductComponentSelection(self))
        self.addPage(PageTaskDetails(self))

    def accept(self):
        """Вызывается при нажатии Finish"""
        if self.field("taskType") == "profile_tool":
            self.create_profile_tool_task()
        else:
            self.create_product_task()
        super().accept()

    def create_profile_tool_task(self):
        deadline = self.field("profileToolDeadline").toString("yyyy-MM-dd")
        description = self.field("profileToolDescription")
        task_data = {
            "profile_tool_id": self.profile_tool['id'],
            "deadline": deadline,
            "created": QDate.currentDate().toString("yyyy-MM-dd"),
            "description": description,
            "status_id": 1
        }
        task = api_manager.api_task.create_task(task_data)
        task_id = task['id']
        for component in self.list_selected_profile_tool_component:
            payload = {"profile_tool_component_id": component['id'], "description": ""}
            api_manager.api_task.create_task_component(task_id, payload)

    def create_product_task(self):
        deadline = self.field("productDeadline").toString("yyyy-MM-dd")
        description = self.field("productDescription")
        task_data = {
            "product_id": self.product['id'],
            "deadline": deadline,
            "created": QDate.currentDate().toString("yyyy-MM-dd"),
            "description": description,
            "status_id": 1
        }
        task = api_manager.api_task.create_task(task_data)
        task_id = task['id']
        for component in self.list_selected_product_component:
            payload = {"product_component_id": component['id'], "description": ""}
            api_manager.api_task.create_task_component(task_id, payload)

class PageStart(QWizardPage):
    def __init__(self, wizard):
        super().__init__()
        self.wizard = wizard
        self.setTitle("Тип задачи")
        self.setSubTitle("Выберите, для чего создается задача")

        layout = QVBoxLayout()
        self.task_type_combo = QComboBox()
        self.task_type_combo.addItems([
            "Задача для инструмента профиля",
            "Задача для изделия"
        ])
        layout.addWidget(QLabel("Тип задачи:"))
        layout.addWidget(self.task_type_combo)
        self.setLayout(layout)

    def nextId(self):
        selected = self.task_type_combo.currentIndex()
        if selected == 0:
            return 1  # Profile → Tool → Components
        else:
            return 4  # Product → Components

class PageProfileSelection(QWizardPage):
    def __init__(self, wizard):
        super().__init__()
        self.wizard = wizard
        self.setTitle("Выбор профиля")
        self.setSubTitle("Введите артикул или описание")

        layout = QVBoxLayout()
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Поиск профиля...")
        self.results_list = QListWidget()

        layout.addWidget(QLabel("Поиск:"))
        layout.addWidget(self.search_edit)
        layout.addWidget(self.results_list)
        self.setLayout(layout)

        self.search_edit.textChanged.connect(self.on_search)

    def on_search(self, text):
        self.results_list.clear()
        if not text.strip():
            return
        results = api_manager.get_search_profile(text)[:10]
        for profile in results:
            item = QListWidgetItem(f"{profile['article']} - {profile['description']}")
            item.setData(Qt.UserRole, profile)
            self.results_list.addItem(item)

    def initializePage(self):
        self.results_list.clear()

    def validatePage(self):
        current_item = self.results_list.currentItem()
        if current_item:
            profile = current_item.data(Qt.UserRole)
            self.wizard.profile = profile
            return True
        return False

    def nextId(self):
        return 2
    

class PageToolSelection(QWizardPage):
    def __init__(self, wizard):
        super().__init__()
        self.wizard = wizard
        self.setTitle("Выбор инструмента")
        self.setSubTitle("Выберите инструмент для профиля")

        layout = QVBoxLayout()
        self.tool_combo = QComboBox()
        layout.addWidget(QLabel("Инструмент:"))
        layout.addWidget(self.tool_combo)
        self.setLayout(layout)

    def initializePage(self):
        self.tool_combo.clear()
        profile = self.wizard.profile
        for pt in profile.get('profile_tool', []):
            name = f"Инструмент {pt['dimension']['name']}"
            self.tool_combo.addItem(name, pt)

    def validatePage(self):
        idx = self.tool_combo.currentIndex()
        if idx >= 0:
            self.wizard.profile_tool = self.tool_combo.itemData(idx)
            return True
        return False

    def nextId(self):
        return 3
    

class PageComponentSelection(QWizardPage):
    def __init__(self, wizard):
        super().__init__()
        self.wizard = wizard
        self.setTitle("Выбор компонентов")
        self.setSubTitle("Отметьте компоненты, которые нужно изготовить")

        layout = QVBoxLayout()
        self.components_list = QListWidget()
        layout.addWidget(self.components_list)
        self.setLayout(layout)

    def initializePage(self):
        self.components_list.clear()
        tool = self.wizard.profile_tool
        for comp in tool['component']:
            status = comp['status']['name']
            if status in ["в разработке", "изготовление"]:
                text = f"{comp['type']['name']} ({status})"
                item = QListWidgetItem()
                checkbox = QCheckBox(text)
                checkbox.setProperty("component", comp)
                item.setSizeHint(checkbox.sizeHint())
                self.components_list.addItem(item)
                self.components_list.setItemWidget(item, checkbox)

    def validatePage(self):
        self.wizard.list_selected_profile_tool_component.clear()
        for i in range(self.components_list.count()):
            item = self.components_list.item(i)
            widget = self.components_list.itemWidget(item)
            if isinstance(widget, QCheckBox) and widget.isChecked():
                comp = widget.property("component")
                self.wizard.list_selected_profile_tool_component.append(comp)
        return len(self.wizard.list_selected_profile_tool_component) > 0

    def nextId(self):
        return 6
    

class PageProductSelection(QWizardPage):
    def __init__(self, wizard):
        super().__init__()
        self.wizard = wizard
        self.setTitle("Выбор изделия")
        self.setSubTitle("Введите название или описание")

        layout = QVBoxLayout()
        self.search_edit = QLineEdit()
        self.results_list = QListWidget()

        layout.addWidget(QLabel("Поиск:"))
        layout.addWidget(self.search_edit)
        layout.addWidget(self.results_list)
        self.setLayout(layout)

        self.search_edit.textChanged.connect(self.on_search)

    def on_search(self, text):
        self.results_list.clear()
        if not text.strip():
            return
        results = api_manager.get_search_product(text)[:10]
        for product in results:
            item = QListWidgetItem(f"{product['name']} - {product['description']}")
            item.setData(Qt.UserRole, product)
            self.results_list.addItem(item)

    def validatePage(self):
        item = self.results_list.currentItem()
        if item:
            self.wizard.product = item.data(Qt.UserRole)
            return True
        return False

    def nextId(self):
        return 5
    

class PageProductComponentSelection(QWizardPage):
    def __init__(self, wizard):
        super().__init__()
        self.wizard = wizard
        self.setTitle("Выбор компонентов изделия")
        self.setSubTitle("Отметьте компоненты для задачи")

        layout = QVBoxLayout()
        self.components_list = QListWidget()
        layout.addWidget(self.components_list)
        self.setLayout(layout)

    def initializePage(self):
        self.components_list.clear()
        for comp in self.wizard.product['component']:
            item = QListWidgetItem()
            checkbox = QCheckBox(comp['name'])
            checkbox.setProperty("component", comp)
            item.setSizeHint(checkbox.sizeHint())
            self.components_list.addItem(item)
            self.components_list.setItemWidget(item, checkbox)

    def validatePage(self):
        self.wizard.list_selected_product_component.clear()
        for i in range(self.components_list.count()):
            item = self.components_list.item(i)
            widget = self.components_list.itemWidget(item)
            if isinstance(widget, QCheckBox) and widget.isChecked():
                comp = widget.property("component")
                self.wizard.list_selected_product_component.append(comp)
        return True

    def nextId(self):
        return 6
    

class PageTaskDetails(QWizardPage):
    def __init__(self, wizard):
        super().__init__()
        self.wizard = wizard
        self.setTitle("Детали задачи")
        self.setSubTitle("Укажите срок и описание")

        layout = QVBoxLayout()

        # Группа для дедлайна и описания
        group = QGroupBox("Параметры задачи")
        group_layout = QVBoxLayout()

        # Дедлайн
        deadline_layout = QVBoxLayout()
        deadline_layout.addWidget(QLabel("Срок выполнения:"))
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate().addDays(7))
        self.date_edit.setCalendarPopup(True)
        deadline_layout.addWidget(self.date_edit)
        group_layout.addLayout(deadline_layout)

        # Описание
        desc_layout = QVBoxLayout()
        desc_layout.addWidget(QLabel("Описание:"))
        self.text_edit = QTextEdit()
        self.text_edit.setMaximumHeight(100)
        desc_layout.addWidget(self.text_edit)
        group_layout.addLayout(desc_layout)

        group.setLayout(group_layout)
        layout.addWidget(group)
        self.setLayout(layout)

    def validatePage(self):
        task_type = self.wizard.field("taskType")
        if task_type == "profile_tool":
            self.setField("profileToolDeadline", self.date_edit.date())
            self.setField("profileToolDescription", self.text_edit.toPlainText())
        else:
            self.setField("productDeadline", self.date_edit.date())
            self.setField("productDescription", self.text_edit.toPlainText())
        return True

    def nextId(self):
        return -1  # Конец