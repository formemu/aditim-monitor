from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QWizardPage, QVBoxLayout,  QListWidget, QListWidgetItem,
                               QCheckBox, QWidget, QComboBox, QHBoxLayout, QLabel)
from ...api_manager import api_manager


class PageProfileToolComponentSelection(QWizardPage):
    def __init__(self, wizard):
        super().__init__()
        self.wizard = wizard

        self.component_to_widget = {}  # component[id]:widget
        self.list_widget = []  # Список виджетов компонентов

        self.setTitle("Выбор компонентов")
        self.setSubTitle("Отметьте компоненты, которые нужно изготовить")
        self.setLayout(QHBoxLayout())

        self.listWidget_component = QListWidget()
        self.container_component = QWidget()
        self.container_component.setLayout(QHBoxLayout())

        self.layout().addWidget(self.listWidget_component)
        self.layout().addWidget(self.container_component)
        

    def initializePage(self):
        self.listWidget_component.clear()
        self.clear_container()
        self.component_to_widget.clear()
        self.list_widget.clear()
        for component in self.wizard.profiletool['component']:
            checkbox = QCheckBox(f"{component['type']['name']}")
            checkbox.setProperty("component", component)
            checkbox.toggled.connect(lambda checked, c=component, cb=checkbox: self.on_component_toggled(checked, c, cb))
            item = QListWidgetItem(self.listWidget_component)
            self.listWidget_component.setItemWidget(item, checkbox)

    def on_component_toggled(self, checked, component, checkbox):
        widget = WidgetGrid(component)
        self.list_widget.append(widget)
        self.component_to_widget[component['id']] = widget
        if self.field("type_id") == 1 and checked:
            # Добавляем виджет в контейнер
            self.container_component.layout().addWidget(widget)

    def clear_container(self):
        """Очищает контейнер"""
        for child in self.container_component.findChildren(QWidget):
            child.deleteLater()

    def validatePage(self):
        self.wizard.list_selected_profiletool_component.clear()
        for i in range(self.listWidget_component.count()):
            item = self.listWidget_component.item(i)
            checkbox = self.listWidget_component.itemWidget(item)
            if isinstance(checkbox, QCheckBox) and checkbox.isChecked():
                component = checkbox.property("component")
                comp_id = component['id']
                list_selected_stage = []
                widget = self.component_to_widget.get(comp_id)
                if widget:
                    layout = widget.layout()
                    for j in range(1, layout.count()):  # пропускаем заголовок
                        sublayout = layout.itemAt(j)
                        checkBox_work_subtype = sublayout.layout().itemAt(0).widget()  # чекбокс
                        comboBox_machine = sublayout.layout().itemAt(1).widget()  # комбобокс
                        if checkBox_work_subtype.isChecked():
                            stage = checkBox_work_subtype.property("stage")
                            machine = comboBox_machine.currentData() if comboBox_machine.isEnabled() else None
                            list_selected_stage.append({ "stage": stage, "machine": machine })

                    component['list_selected_stage'] = list_selected_stage
                    self.wizard.list_selected_profiletool_component.append(component)

        return len(self.wizard.list_selected_profiletool_component)

    def nextId(self):
        return self.wizard.PAGE_TASK_DETAILS

class WidgetGrid(QWidget):
    def __init__(self, component, parent=None):
        super().__init__(parent)

        self.setLayout(QVBoxLayout())
        title = QLabel(f"{component['type']['name']}")
        self.layout().addWidget(title)
        # Загружаем этапы
        list_stage = self.load_stage(component)
        for stage in list_stage:
            layout = QHBoxLayout()
            # Чекбокс операции
            checkBox_stage = QCheckBox(f"{stage['stage_num']}. {stage['work_subtype']['name']}")
            checkBox_stage.setProperty("stage", stage)
            layout.addWidget(checkBox_stage)
            # ComboBox со станками
            comboBox_machine = QComboBox()
            # comboBox_machine.setProperty("stage", stage)
            comboBox_machine.setEnabled(False)
            list_machine = [
                machine for machine in api_manager.directory['machine']
                if machine['work_type_id'] == stage['work_subtype']['work_type_id']
            ]
            for machine in list_machine:
                comboBox_machine.addItem(f"{machine['name']}", machine)

            if list_machine:
                comboBox_machine.setCurrentIndex(0)
                comboBox_machine.setEnabled(True)
            else:
                comboBox_machine.setVisible(False)

            layout.addWidget(comboBox_machine)
            # Активация комбобокса при чеке
            checkBox_stage.toggled.connect(lambda checked, c=comboBox_machine: c.setEnabled(checked))
            # Добавляем строку в основной layout
            self.layout().addLayout(layout)

    def load_stage(self, component):
        profiletool_component_type_id = component['type']['id']
        list_stage = []
        for stage in api_manager.plan['task_component_stage']:
            if stage['profiletool_component_type']['id'] == profiletool_component_type_id:
                list_stage.append(stage)
        list_stage.sort(key=lambda x: x['stage_num'])
        return list_stage