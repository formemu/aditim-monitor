"""Мастер создания задачи"""
from PySide6.QtWidgets import QWizard
from PySide6.QtCore import QFile, QDate
from PySide6.QtUiTools import QUiLoader
from ...constant import UI_PATHS_ABS, get_style_path
from ...api_manager import api_manager
from ...style_util import load_styles
from .page_profiletool_selection import PageProfiletoolSelection
from .page_profiletool_component_dev import PageProfiletoolComponentDev
from .page_profiletool_component_prod import PageProfiletoolComponentProd
from .page_profiletool_component_rev import PageProfiletoolComponentRev
from .page_profiletool_blank import PageProfiletoolBlank

# Константы
PAGE = {
    "START": 0,
    "PROFILETOOL_SELECTION": 1,
    "PROFILETOOL_COMPONENT_DEV": 2,
    "PROFILETOOL_COMPONENT_SELECTION": 3,
    "PROFILETOOL_COMPONENT_REV": 4,
    "PROFILETOOL_BLANK": 5,
    "PRODUCT_SELECTION": 6,
    "PRODUCT_COMPONENT_SELECTION": 7,
    "TASK_DETAIL": 8
}

class WizardTaskCreate(QWizard):
    """Мастер создания задачи"""
    def __init__(self, parent=None):
        super().__init__(parent)
        # Состояние
        self.profileTool = None
        self.product = None
        self.task_data = {
            "status_id": 1,
            "location_id": 1,
            "created": QDate.currentDate().toString("yyyy-MM-dd"),
            "component": list()
        }
        self.load_ui()
        
        # Инициализация страниц
        self.page_profiletool_selection = PageProfiletoolSelection(self, self.ui)
        self.page_profiletool_component_dev = PageProfiletoolComponentDev(self, self.ui)
        self.page_profiletool_component_prod = PageProfiletoolComponentProd(self, self.ui)
        self.page_profiletool_component_rev = PageProfiletoolComponentRev(self, self.ui)
        self.page_profiletool_blank = PageProfiletoolBlank(self, self.ui)
        
        self.setup_ui()
        self.setWizardStyle(QWizard.WizardStyle.ClassicStyle)
    
    def load_ui(self):
        """Загрузка UI из файла"""
        ui_file = QFile(UI_PATHS_ABS["WIZARD_TASK_CREATE"])
        ui_file.open(QFile.ReadOnly)
        loader = QUiLoader()
        self.ui = loader.load(ui_file)
        ui_file.close()

    def setup_ui(self):
        """Настраивает логику визарда."""
        self.setStyleSheet(load_styles(get_style_path("WIZARDS")))
        self.addPage(self.ui.wizardPage_start)
        self.addPage(self.ui.wizardPage_profiletool_selection)
        self.addPage(self.ui.wizardPage_profiletool_component_dev)
        self.addPage(self.ui.wizardPage_profiletool_component_selection)
        self.addPage(self.ui.wizardPage_profiletool_component_rev)
        self.addPage(self.ui.wizardPage_profiletool_blank)
        self.addPage(self.ui.wizardPage_product_selection)
        self.addPage(self.ui.wizardPage_product_component_selection)
        self.addPage(self.ui.wizardPage_task_detail)
        self.currentIdChanged.connect(self.on_page_changed)
        self.setStartId(0)

        self.ui.dateEdit_date.setDate(QDate.currentDate().addDays(14))
        
        self.load_comboBox_task_type()

    def on_page_changed(self, id: int):
        """Обработчик изменения текущей страницы"""
        if id == PAGE["START"]:
            pass
        elif id == PAGE["PROFILETOOL_COMPONENT_DEV"]:
            self.page_profiletool_component_dev.load()
        elif id == PAGE["PROFILETOOL_COMPONENT_SELECTION"]:
            self.page_profiletool_component_prod.load()
        elif id == PAGE["PROFILETOOL_COMPONENT_REV"]:
            self.page_profiletool_component_rev.load()
        elif id == PAGE["PROFILETOOL_BLANK"]:
            self.page_profiletool_blank.load()
        elif id == PAGE["TASK_DETAIL"]:
            self.task_data["type_id"] = self.ui.comboBox_work_type.currentIndex()
            self.create_list_profiletool_component_selected()

    def nextId(self):
        """Переопределяем маршрут переходов между страницами."""
        if self.currentId() == PAGE["START"]:
            if self.ui.comboBox_product_type.currentIndex() == 0:
                return PAGE["PROFILETOOL_SELECTION"]
            else:
                return PAGE["PRODUCT_SELECTION"]
        elif self.currentId() == PAGE["PROFILETOOL_SELECTION"]:
            if self.ui.comboBox_work_type.currentIndex() == 0:
                return PAGE["PROFILETOOL_COMPONENT_DEV"]
            elif self.ui.comboBox_work_type.currentIndex() == 1:
                return PAGE["PROFILETOOL_COMPONENT_SELECTION"]
            elif self.ui.comboBox_work_type.currentIndex() == 2:
                return PAGE["PROFILETOOL_COMPONENT_REV"]
            elif self.ui.comboBox_work_type.currentIndex() == 3:
                return PAGE["PROFILETOOL_BLANK"]
        elif self.currentId() == PAGE["PROFILETOOL_COMPONENT_DEV"]:
            return PAGE["TASK_DETAIL"]
        elif self.currentId() == PAGE["PROFILETOOL_COMPONENT_REV"]:
            return PAGE["TASK_DETAIL"]  
        elif self.currentId() == PAGE["PROFILETOOL_COMPONENT_SELECTION"]:
            return PAGE["TASK_DETAIL"]
        elif self.currentId() == PAGE["PROFILETOOL_BLANK"]:
            return PAGE["TASK_DETAIL"]
        elif self.currentId() == PAGE["PRODUCT_SELECTION"]:
            return PAGE["PRODUCT_COMPONENT_SELECTION"]
        elif self.currentId() == PAGE["PRODUCT_COMPONENT_SELECTION"]:
            return PAGE["TASK_DETAIL"]
        elif self.currentId() == PAGE["TASK_DETAIL"]:
            return -1
        return 0

    # --- Страница выбора типа изделия ---
    def load_comboBox_task_type(self):
        """запонляет выбор типа работ"""
        for type in api_manager.directory['task_type']:
            self.ui.comboBox_work_type.addItem(type['name'], type['id'])

    def create_list_profiletool_component_selected(self):
        """Получает выбранные компоненты из страниц"""
        # Для задач с заготовками компоненты обрабатываются отдельно
        if self.task_data['type_id'] == 3:
            return
        
        # Получаем компоненты через страницы
        if self.task_data['type_id'] == 0:
            selected_components = self.page_profiletool_component_dev.get_selected_component()
        elif self.task_data['type_id'] == 1:
            selected_components = self.page_profiletool_component_prod.get_selected_component()
        elif self.task_data['type_id'] == 2:
            selected_components = self.page_profiletool_component_rev.get_selected_component()
        else:
            selected_components = []
        
        self.task_data["component"] = selected_components

    # --- Создание задач ---
    def accept(self):
        self.task_data['description'] = self.ui.textEdit_description.toPlainText()
        self.task_data['deadline'] = self.ui.dateEdit_date.date().toString("yyyy-MM-dd")
        self.task_data['created'] = QDate.currentDate().toString("yyyy-MM-dd")
        if self.task_data["profiletool_id"]:
            if self.task_data['type_id'] == 0:
                self.create_profiletool_task_dev()
            elif self.task_data['type_id'] == 1:
                self.create_profiletool_task_prod()
            elif self.task_data['type_id'] == 2:
                self.create_profiletool_task_rev()
            elif self.task_data['type_id'] == 3:
                self.create_profiletool_task_blank()
        elif self.task_data["product_id"]:
            self.create_product_task()
        super().accept()

    def create_profiletool_task_dev(self):
        task = api_manager.api_task.create_task(self.task_data)
        for component in self.task_data["component"]:
            component_data = {"profiletool_component_id": component['id']}
            api_manager.api_task.create_task_component(task['id'], component_data)


    def create_profiletool_task_prod(self):
        task = api_manager.api_task.create_task(self.task_data)
        for component in self.task_data["component"]:
            component_data = {"profiletool_component_id": component['id']}
            task_component = api_manager.api_task.create_task_component(task['id'], component_data)
            task_component_id = task_component['id']
            for selected_stage in component['stage']:
                stage = {
                    "work_subtype_id": selected_stage['work_subtype']['id'],
                    "stage_num": selected_stage['stage_num']
                }
                api_manager.api_task.create_task_component_stage(task_component_id, stage)

    def create_profiletool_task_rev(self):
        task = api_manager.api_task.create_task(self.task_data)
        for component in self.task_data["component"]:
            component_data = {"profiletool_component_id": component['id']}
            api_manager.api_task.create_task_component(task['id'], component_data)

    def create_profiletool_task_blank(self):
        """Создание задачи для изготовления заготовок"""
        task = api_manager.api_task.create_task(self.task_data)
        
        # Получаем параметры заготовок через страницу
        blank_data_list = self.page_profiletool_blank.get_blank_data_list()
        
        for blank_data in blank_data_list:
            if not blank_data:
                continue  # Пропускаем, если заготовка не выбрана
            
            component_id = blank_data['component_id']
            blank_id = blank_data['blank_id']
            
            # Создаем task_component
            component_data = {"profiletool_component_id": component_id}
            task_component = api_manager.api_task.create_task_component(task['id'], component_data)
            
            # Обновляем заготовку: привязываем к компоненту и добавляем размеры детали
            blank_update_data = {
                "profiletool_component_id": component_id,
                "product_width": blank_data['product_width'],
                "product_height": blank_data['product_height'],
                "product_length": blank_data['product_length']
            }
            api_manager.api_blank.update_blank(blank_id, blank_update_data)

