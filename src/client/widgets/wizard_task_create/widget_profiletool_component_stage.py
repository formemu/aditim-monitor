"""Виджет выбора этапов работ для компонента"""
from PySide6.QtWidgets import QWidget, QCheckBox
from PySide6.QtCore import QFile
from PySide6.QtUiTools import QUiLoader
from ...constant import UI_PATHS_ABS
from ...api_manager import api_manager


class WidgetProfiletoolComponentStage(QWidget):
    """Виджет выбора этапов работ для компонента инструмента профиля"""
    
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
        """Настройка UI и загрузка этапов"""
        self.ui.label_component_name.setText(self.component['type']['name'])
        self.component.setdefault('stage', [])
        
        # Загружаем и отображаем этапы
        list_stage = self.load_list_component_stage()
        for stage in list_stage:
            checkbox = QCheckBox()
            checkbox.setText(f"{stage['stage_num']} {stage['work_subtype']['name']}")
            checkbox.setProperty("stage", stage)
            checkbox.setChecked(True)
            checkbox.toggled.connect(lambda checked, s=stage: self.on_stage_toggled(checked, s))
            self.ui.widget_comboBox.layout().addWidget(checkbox)
            self.component['stage'].append(stage)

    def load_list_component_stage(self):
        """Загрузка списка этапов для типа компонента"""
        comp_type_id = self.component['type']['id']
        list_stage = []
        for stage in api_manager.plan.get('task_component_stage', []):
            if stage['profiletool_component_type']['id'] == comp_type_id:
                list_stage.append(stage)
        return list_stage

    def on_stage_toggled(self, checked, stage):
        """Обработка включения/отключения этапа"""
        if checked:
            if stage not in self.component['stage']:
                self.component['stage'].append(stage)
        else:
            if stage in self.component['stage']:
                self.component['stage'].remove(stage)
