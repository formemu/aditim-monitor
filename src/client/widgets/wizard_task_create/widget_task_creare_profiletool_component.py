from PySide6.QtWidgets import QWidget, QCheckBox
from PySide6.QtCore import QFile
from PySide6.QtUiTools import QUiLoader
from ...constant import UI_PATHS_ABS
from ...api_manager import api_manager

class WidgetTaskCreateProfiletoolComponent(QWidget):
    """Виджет создания компонента инструмента профиля"""
    def __init__(self, component: dict, parent=None):
        super().__init__(parent)
        self.component = component
        self.load_ui()
        self.setup_ui()
        
    
    def load_ui(self):
        """Загрузка UI из файла"""
        ui_file = QFile(UI_PATHS_ABS["WIDGET_TASK_CREATE_PROFILETOOL_COMPONENT"])
        ui_file.open(QFile.ReadOnly)
        loader = QUiLoader()
        self.ui = loader.load(ui_file)
        ui_file.close()
        self.setLayout(self.ui.layout())

    def setup_ui(self):
        """Настраивает логику визарда."""
        self.ui.label_component_name.setText(self.component['type']['name'])
        self.load_list_profiletool_component_stage(self.component)
        for stage in self.load_list_profiletool_component_stage(self.component):
            checkbox = QCheckBox()
            checkbox.setText(f"{stage['stage_num']} {stage['work_subtype']['name']}")
            checkbox.setProperty("stage", stage)
            checkbox.setChecked(True)
            checkbox.toggled.connect(lambda checked, stage=stage, chechBox=checkbox: 
                                    self.activate_component_stage(checked, stage))
            self.ui.widget_comboBox.layout().addWidget(checkbox)
            self.component['stage'].append(stage)

    def load_list_profiletool_component_stage(self, component):
        comp_type_id = component['type']['id']
        list_stage = []
        for stage in api_manager.plan.get('task_component_stage', []):
            if stage['profiletool_component_type']['id'] == comp_type_id:
                list_stage.append(stage)
        return list_stage

    def activate_component_stage(self, checked, stage):
        if checked:
            self.component['stage'].append(stage)

        else:
            self.component['stage'].remove(stage)
