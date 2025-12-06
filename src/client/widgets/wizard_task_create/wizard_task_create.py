"""Мастер создания задачи"""
from PySide6.QtWidgets import QWizard, QListWidgetItem, QWidget, QCheckBox
from PySide6.QtCore import QFile, Qt, QDate
from PySide6.QtUiTools import QUiLoader
from ...constant import UI_PATHS_ABS, get_style_path
from ...api_manager import api_manager
from ...style_util import load_styles
from .widget_task_creare_profiletool_component import WidgetTaskCreateProfiletoolComponent

# Константы
PAGE = {
    "START": 0,
    "PROFILETOOL_SELECTION": 1,
    "PROFILETOOL_COMPONENT_DEV": 2,
    "PROFILETOOL_COMPONENT_SELECTION": 3,
    "PROFILETOOL_COMPONENT_REV": 4,
    "PRODUCT_SELECTION": 5,
    "PRODUCT_COMPONENT_SELECTION": 6,
    "TASK_DETAIL": 7
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
        self.addPage(self.ui.wizardPage_product_selection)
        self.addPage(self.ui.wizardPage_product_component_selection)
        self.addPage(self.ui.wizardPage_task_detail)
        self.currentIdChanged.connect(self.on_page_changed)
        self.setStartId(0)

        self.ui.dateEdit_date.setDate(QDate.currentDate().addDays(14))

        # Сигналы поиска
        self.ui.lineEdit_profile_search.textChanged.connect(self.on_search_profile)
        self.ui.lineEdit_profile_search.returnPressed.connect(self.on_profile_selected)

        # Выбор из результатов
        self.ui.listWidget_profile_search.itemSelectionChanged.connect(self.on_profile_selected)
        self.ui.listWidget_profile_search.itemClicked.connect(lambda _: self.on_profile_selected())
        

        self.load_comboBox_task_type()

    def on_page_changed(self, id: int):
        """Обработчик изменения текущей страницы"""
        if id == PAGE["START"]:
            pass
        elif id == PAGE["PROFILETOOL_COMPONENT_DEV"]:
            self.load_profiletool_component_dev()
        elif id == PAGE["PROFILETOOL_COMPONENT_SELECTION"]:
            self.load_profiletool_component_prod()
        elif id == PAGE["PROFILETOOL_COMPONENT_REV"]:
            self.load_profiletool_component_rev()
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
        elif self.currentId() == PAGE["PROFILETOOL_COMPONENT_DEV"]:
            return PAGE["TASK_DETAIL"]
        elif self.currentId() == PAGE["PROFILETOOL_COMPONENT_REV"]:
            return PAGE["TASK_DETAIL"]  
        elif self.currentId() == PAGE["PROFILETOOL_COMPONENT_SELECTION"]:
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

    # --- Страница выбора инструмента профиля ---
    def on_search_profile(self, text: str):
        """поиск профиля по артиклу"""
        self.ui.listWidget_profile_search.clear()
        for profile in api_manager.search_in('profile', 'article', text)[:10]:
            item = QListWidgetItem(f"{profile['article']}")
            item.setData(Qt.UserRole, profile)
            self.ui.listWidget_profile_search.addItem(item)

    def on_profile_selected(self):
        item = self.ui.listWidget_profile_search.currentItem()
        if not item:
            return
        self.task_data["profile"] = item.data(Qt.UserRole)
        self.ui.lineEdit_profile_search.setText(f"{self.task_data['profile']['article']}")
        self.ui.comboBox_dimension.clear()
        for profiletool in self.task_data["profile"]['profiletool']:
            name = profiletool['dimension']['name']
            self.ui.comboBox_dimension.addItem(name, profiletool)

        self.ui.comboBox_dimension.currentIndexChanged.connect(self.on_dimension_selected)
    
    def on_dimension_selected(self):
        if self.ui.comboBox_dimension.currentIndex() == -1:
            self.profileTool = None
        else:
            self.profileTool = self.ui.comboBox_dimension.currentData()
            self.task_data["profiletool_id"] = self.profileTool['id']

    # --- Страница выбора компонентов для разработки ---
    def load_profiletool_component_dev(self):
        """Загружает компоненты для разработки"""
        self.ui.listWidget_profiletool_component_dev.clear()
        for component in self.profileTool['component']:
            item = QListWidgetItem()
            checkbox = QCheckBox(f"{component['type']['name']}")
            checkbox.setProperty("component_id", component['id'])
            self.ui.listWidget_profiletool_component_dev.addItem(item)
            self.ui.listWidget_profiletool_component_dev.setItemWidget(item, checkbox)

    # --- Страница выбора компонентов инструментов и работ ---
    def load_profiletool_component_prod(self):
        self.ui.listWidget_profiletool_component_prod.clear()    
        for child in self.ui.widget_profiletool_component_container.findChildren(QWidget):
            child.deleteLater()
        for component in self.profileTool['component']:
            component.setdefault('stage', [])
            item = QListWidgetItem("")
            item.setData(Qt.UserRole, component)
            self.ui.listWidget_profiletool_component_prod.addItem(item)
            checkbox = QCheckBox(f"{component['type']['name']}")
            checkbox.setProperty("component_id", component['id'])
            checkbox.toggled.connect(lambda checked, comp=component, checkBox=checkbox: 
                                     self.activate_profiletool_component(checked, comp))
            self.ui.listWidget_profiletool_component_prod.setItemWidget(item, checkbox)

    def activate_profiletool_component(self, checked, component):
        layout = self.ui.widget_profiletool_component_container.layout()
        if checked:
            widget_component = WidgetTaskCreateProfiletoolComponent(component)
            layout.addWidget(widget_component)
        else:
            layout.removeWidget(widget_component)
            widget_component.deleteLater()

    def create_list_profiletool_component_selected(self):
        if self.task_data['type_id'] == 0:
            listWidget_selected = self.ui.listWidget_profiletool_component_dev
        elif self.task_data['type_id'] == 1:
            listWidget_selected = self.ui.listWidget_profiletool_component_prod
        elif self.task_data['type_id'] == 2:
            listWidget_selected = self.ui.listWidget_profiletool_component_rev

        for i in range(listWidget_selected.count()):
            item = listWidget_selected.item(i)
            checkBox = listWidget_selected.itemWidget(item)
            if checkBox.isChecked():
                component_id = checkBox.property("component_id")
                component = None
                for comp in self.profileTool['component']:
                    if comp.get('id') == component_id:
                        component = comp
                        break
                self.task_data["component"].append(component)

    # --- Страница выбора компонентов для изменения ---
    def load_profiletool_component_rev(self):
        """Загружает компоненты для изменения"""
        self.ui.listWidget_profiletool_component_rev.clear()
        for component in self.profileTool['component']:
            item = QListWidgetItem("")
            checkbox = QCheckBox(f"{component['type']['name']}")
            checkbox.setProperty("component_id", component['id'])
            self.ui.listWidget_profiletool_component_rev.addItem(item)
            self.ui.listWidget_profiletool_component_rev.setItemWidget(item, checkbox)

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

