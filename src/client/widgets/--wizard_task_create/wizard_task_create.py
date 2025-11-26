"""Мастер создания задачи"""
from PySide6.QtWidgets import QWizard, QListWidgetItem, QWidget, QHBoxLayout, QVBoxLayout, QCheckBox, QLabel
from PySide6.QtCore import QFile, Qt, QDate
from PySide6.QtUiTools import QUiLoader
from ...constant import UI_PATHS_ABS, get_style_path
from ...api_manager import api_manager
from ...style_util import load_styles
from .widget_task_creare_profiletool_component import WidgetTaskCreateProfiletoolComponent


class WizardTaskCreate(QWizard):
    """Мастер создания задачи"""
    def __init__(self, parent=None):
        super().__init__(parent)
        # Состояние
        self.task_data = {
            "status_id": 1,
            "location_id": 1,
            "created": QDate.currentDate().toString("yyyy-MM-dd"),
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
        self.addPage(self.ui.wizardPage_profiletool_component_selection)
        self.addPage(self.ui.wizardPage_product_selection)
        self.addPage(self.ui.wizardPage_product_component_selection)
        self.addPage(self.ui.wizardPage_task_detail)
        self.currentIdChanged.connect(self.on_id_changed)
        self.setStartId(0)
        
        # Сигналы поиска
        self.ui.lineEdit_profile_search.textChanged.connect(self.on_search_profile)
        self.ui.lineEdit_profile_search.returnPressed.connect(self.on_profile_selected)

        # Выбор из результатов
        self.ui.listWidget_profile_search.itemSelectionChanged.connect(self.on_profile_selected)
        self.ui.listWidget_profile_search.itemClicked.connect(lambda _: self.on_profile_selected())
        self.ui.comboBox_dimension.currentIndexChanged.connect(self.on_dimension_selected)

        self.load_comboBox_task_type()

    def on_id_changed(self, pid: int):
        if pid == 0:
            self.task_data["type_id"] = self.ui.comboBox_work_type.currentData()
        elif pid == 2:
            self.load_profiletool_component() 

    def nextId(self):
        """Переопределяем маршрут переходов между страницами."""
        if self.currentId() == 0:
            if self.ui.comboBox_product_type.currentIndex() == 0:
                return 1
            else:
                return 3
        elif self.currentId() == 1:
            return 2
        elif self.currentId() == 2:
            return 5
        elif self.currentId() == 3:
            return 4
        elif self.currentId() == 4:
            return 5
        elif self.currentId() == 5:
            return -1


    def load_comboBox_task_type(self):
        """запонляет выбор типа работ"""
        for type in api_manager.directory['task_type']:
            self.ui.comboBox_work_type.addItem(type['name'], type['id'])

    def on_search_profile(self, text: str):
        """поиск профиля по артиклу"""
        self.ui.listWidget_profile_search.clear()
        for profile in api_manager.search_in('profile', 'article', text)[:10]:
            item = QListWidgetItem(f"{profile['article']}")
            item.setData(Qt.UserRole, profile)
            self.ui.listWidget_profile_search.addItem(item)

    def on_profile_selected(self):
        item = self.ui.listWidget_profile_search.currentItem()
        self.task_data["profile"] = item.data(Qt.UserRole)
        self.ui.lineEdit_profile_search.setText(f"{self.task_data['profile']['article']}")
        self.ui.comboBox_dimension.clear()
        for profiletool in self.task_data["profile"]['profiletool']:
            name = profiletool['dimension']['name']
            self.ui.comboBox_dimension.addItem(name, profiletool)
    
    def on_dimension_selected(self):
        self.task_data["profiletool"] = self.ui.comboBox_dimension.currentData()

    # --- Страница выбора компонентов инструментов и работ ---
    def load_profiletool_component(self):
        self.ui.listWidget_profiletool_component.clear()    
        for child in self.ui.widget_profiletool_component_container.findChildren(QWidget):
            child.deleteLater()
        self.component_id_to_widget = {}
        for component in self.task_data["profiletool"]['component']:
            item = QListWidgetItem(f"{component['type']['name']}")
            item.setData(Qt.UserRole, component)
            self.ui.listWidget_profiletool_component.addItem(item)
            checkbox = QCheckBox(f"{component['type']['name']}")
            checkbox.setProperty("component", component)
            checkbox.toggled.connect(lambda checked, comp=component, chechBox=checkbox: 
                                     self.activate_profiletool_component(checked, comp))
            self.ui.listWidget_profiletool_component.setItemWidget(item, checkbox)

    def activate_profiletool_component(self, checked, component):
        layout = self.ui.widget_profiletool_component_container.layout()
        if checked:
            widget_component = WidgetTaskCreateProfiletoolComponent(component)

            self.component_id_to_widget[component['id']] = widget_component
            layout.addWidget(widget_component)
        else:
            widget_component = self.component_id_to_widget.pop(component['id'], None)
            if widget_component:
                layout.removeWidget(widget_component)
                widget_component.deleteLater()

        # Сортировка по type_id
        list_widget_component = []
        for i in range(layout.count()):
            w = layout.itemAt(i).widget()
            if w:
                list_widget_component.append((w.property("type_id") or 0, w))
        list_widget_component.sort(key=lambda x: x[0])
        for _, w in list_widget_component:
            layout.removeWidget(w)
            layout.addWidget(w)



    def load_list_profiletool_component_stage(self, component):
        comp_type_id = component['type']['id']
        list_stage = []
        for stage in api_manager.plan.get('task_component_stage', []):
            if stage['profiletool_component_type']['id'] == comp_type_id:
                list_stage.append(stage)
        list_stage.sort(key=lambda s: s['stage_num'])
        return list_stage

    def create_list_profiletool_component_selected(self):
        for i in range(self.ui.listWidget_profiletool_component.count()):
            item = self.ui.listWidget_profiletool_component.item(i)
            checkBox = self.ui.listWidget_profiletool_component.itemWidget(item)
            if checkBox.isChecked():
                component = checkBox.property("component")
                # Найти соответствующий виджет
                widget = self.component_id_to_widget[component['id']]
                if widget and widget.layout():
                    layout = widget.layout()
                    for j in range(1, layout.count()):
                        sublayout = layout.itemAt(j)
                        if not sublayout or not sublayout.layout():
                            continue
                        cb_widget = sublayout.layout().itemAt(0).widget()
                        if isinstance(cb_widget, QCheckBox) and cb_widget.isChecked():
                            stage = cb_widget.property("stage")
                            component["list_selected_stage"].append({"stage": stage})
                self.task_data["component"].append(component)

    # --- Создание задач ---
    def accept(self):
        if self.task_data["profiletool"]:
            self.create_profiletool_task()
        elif self.task_data["product"]:
            self.create_product_task()
        super().accept()

    def create_profiletool_task(self):
        task = api_manager.api_task.create_task(self.task_data)
        for component in self.task_data["component"]:
            component_data = {"profiletool_component_id": component['id']}
            task_component = api_manager.api_task.create_task_component(task['id'], component_data)
            task_component_id = task_component['id']
            for selected_stage in component['list_selected_stage']:
                stage = {
                    "work_subtype_id": selected_stage['stage']['work_subtype']['id'],
                    "stage_num": selected_stage['stage']['stage_num']
                }
                api_manager.api_task.create_task_component_stage(task_component_id, stage)
 
