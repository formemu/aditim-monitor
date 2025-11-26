from PySide6.QtCore import QDate
from PySide6.QtWidgets import QWizard

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
    PAGE_PROFILETOOL_SELECTION = 2
    PAGE_PROFILETOOL_COMPONENT_SELECTION = 3
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
        self.profiletool = None
        self.product = None
        self.dict_selected_profiletool_component = []
        self.dict_selected_product_component = []



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
        if self.profiletool:
            self.create_profiletool_task()
        elif self.product:
            self.create_product_task()
        super().accept()

    def create_profiletool_task(self):
        deadline = self.field("deadline").toString("yyyy-MM-dd")
        description = self.field("description")
        type_id = self.field("type_id")

        task_data = {
            "profiletool_id": self.profiletool['id'],
            "deadline": deadline,
            "created": QDate.currentDate().toString("yyyy-MM-dd"),
            "description": description,
            "status_id": 1,
            "type_id": type_id,
            "location_id": 1
        }
        task = api_manager.api_task.create_task(task_data)
        task_id = task['id']
        for component in self.dict_selected_profiletool_component:
            # 1. Создаём компонент задачи
            component_data = {"profiletool_component_id": component['id'], "description": ""}
            task_component = api_manager.api_task.create_task_component(task_id, component_data)
            task_component_id = task_component['id']

            # 2. Создаём этапы (если есть)
            list_selected_stage = component['list_selected_stage']
            for selected_stage in list_selected_stage:
                stage = {
                    "work_subtype_id": selected_stage['stage']['work_subtype']['id'],
                    # "machine_id": selected_stage['machine']['id'] if selected_stage['machine'] else None,
                    "stage_num": selected_stage['stage']['stage_num']
                }
                try:
                    api_manager.api_task.create_task_component_stage(task_component_id, stage)
                except Exception as e:
                    print(f"Ошибка при создании этапа: {e}")

    def create_product_task(self):
        deadline = self.field("deadline").toString("yyyy-MM-dd")
        description = self.field("description")
        type_id = self.field("type_id")
        task_data = {
            "product_id": self.product['id'],
            "deadline": deadline,
            "created": QDate.currentDate().toString("yyyy-MM-dd"),
            "description": description,
            "status_id": 1,
            "type_id": type_id,
            "location_id": 1
        }
        task = api_manager.api_task.create_task(task_data)
        task_id = task['id']
        for component in self.dict_selected_product_component:
            component_data = {"product_component_id": component['id'], "description": ""}
            api_manager.api_task.create_task_component(task_id, component_data)

    

