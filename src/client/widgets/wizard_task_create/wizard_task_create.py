from PySide6.QtCore import QDate
from PySide6.QtWidgets import (QWizard)

from ...api_manager import api_manager

from .page_start import PageStart
from .page_profile_selection import PageProfileSelection
from .page_profiletool_selection import PageProfileToolSelection
from .page_profiletool_component_selection import PageProfileToolComponentSelection
from .page_product_component_selection import PageProductComponentSelection
from .page_product_selection import PageProductSelection
from .page_task_detail import PageTaskDetails


class WizardTaskCreate(QWizard):
        # Константы для ID страниц
    PAGE_START = 0
    PAGE_PROFILE_SELECTION = 1
    PAGE_PROFILE_TOOL_SELECTION = 2
    PAGE_PROFILE_TOOL_COMPONENT_SELECTION = 3
    PAGE_PRODUCT_SELECTION = 4
    PAGE_PRODUCT_COMPONENT_SELECTION = 5
    PAGE_TASK_DETAILS = 6

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Создание задачи")
        self.setWizardStyle(QWizard.ModernStyle)
        self.setMinimumSize(400, 300)

        # Общие данные
        self.profile = None
        self.profile_tool = None
        self.product = None
        self.list_selected_profile_tool_component = []
        self.list_selected_product_component = []

        # Добавляем страницы — ID присваиваются по порядку: 0, 1, 2...
        self.addPage(PageStart(self))                           # → ID = 0
        self.addPage(PageProfileSelection(self))                # → ID = 1
        self.addPage(PageProfileToolSelection(self))            # → ID = 2
        self.addPage(PageProfileToolComponentSelection(self))   # → ID = 3
        self.addPage(PageProductSelection(self))                # → ID = 4
        self.addPage(PageProductComponentSelection(self))       # → ID = 5
        self.addPage(PageTaskDetails(self))                     # → ID = 6

    def accept(self):
        """Вызывается при нажатии Finish"""
        if self.profile_tool:
            self.create_profile_tool_task()
        elif self.product:
            self.create_product_task()
        super().accept()

    def create_profile_tool_task(self):
        deadline = self.field("deadline").toString("yyyy-MM-dd")
        description = self.field("description")
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
            print(component)
            component_data = {"profile_tool_component_id": component['id'], "description": ""}
            api_manager.api_task.create_task_component(task_id, component_data)

    def create_product_task(self):
        deadline = self.field("deadline").toString("yyyy-MM-dd")
        description = self.field("description")
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
            component_data = {"product_component_id": component['id'], "description": ""}
            api_manager.api_task.create_task_component(task_id, component_data)

    

