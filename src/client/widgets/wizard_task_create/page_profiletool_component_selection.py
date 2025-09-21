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
        for component in self.wizard.profile_tool['component']:
            checkbox = QCheckBox(f"{component['type']['name']}")
            checkbox.setProperty("component", component)
            checkbox.toggled.connect(lambda checked, c=component, cb=checkbox: self.on_component_toggled(checked, c, cb))
            item = QListWidgetItem(self.listWidget_component)
            self.listWidget_component.setItemWidget(item, checkbox)

    def on_component_toggled(self, checked, component, checkbox):
        if checked:
            widget = WidgetGrid(component)
            self.list_widget.append(widget)
            self.component_to_widget[component['id']] = widget
            # Добавляем виджет в контейнер
            self.container_component.layout().addWidget(widget)
        else:
            widget = self.component_to_widget.pop(component['id'], None)
            if widget and widget in self.list_widget:
                self.list_widget.remove(widget)
                # Удаляем виджет из контейнера
                widget.setParent(None)
                widget.deleteLater()

    def clear_container(self):
        """Очищает контейнер"""
        for child in self.container_component.findChildren(QWidget):
            child.deleteLater()

    def validatePage(self):
        self.wizard.list_selected_profile_tool_component.clear()
        for i in range(self.listWidget_component.count()):
            item = self.listWidget_component.item(i)
            checkbox = self.listWidget_component.itemWidget(item)
            if isinstance(checkbox, QCheckBox) and checkbox.isChecked():
                component = checkbox.property("component")
                comp_id = component['id']

                selected_stages = []
                widget = self.component_to_widget.get(comp_id)
                if widget:
                    layout = widget.layout()
                    for j in range(1, layout.count()):  # пропускаем заголовок
                        sublayout = layout.itemAt(j)
                        if sublayout and sublayout.layout():
                            cb = sublayout.layout().itemAt(0).widget()  # чекбокс
                            combo = sublayout.layout().itemAt(1).widget()  # комбобокс
                            if isinstance(cb, QCheckBox) and cb.isChecked():
                                stage = cb.property("stage")
                                machine = combo.currentData() if combo.isEnabled() else None
                                selected_stages.append({
                                    "stage": stage,
                                    "machine": machine
                                })

                component['list_selected_stage'] = selected_stages
                self.wizard.list_selected_profile_tool_component.append(component)

        return len(self.wizard.list_selected_profile_tool_component) > 0

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
            checkBox_stage = QCheckBox(f"{stage['stage_num']}. {stage['name']}")
            checkBox_stage.setProperty("stage", stage)
            layout.addWidget(checkBox_stage)
            # ComboBox со станками
            comboBox_machine = QComboBox()
            comboBox_machine.setProperty("stage", stage)
            comboBox_machine.setEnabled(False)
            list_machine = [
                machine for machine in api_manager.directory['machine']
                if machine['work_type_id'] == stage['work_type_id']
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

        for item in api_manager.plan['task_component_stage']:
            if item['profiletool_component_type']['id'] == profiletool_component_type_id:
                work_subtype = item['work_subtype']
                list_stage.append({
                    "name": work_subtype['name'],
                    "id": work_subtype['id'],
                    "stage_num": item['stage_num'],
                    "description": work_subtype.get('description', ''),
                    "work_type_id": work_subtype.get('work_type_id')
                })

        list_stage.sort(key=lambda x: x['stage_num'])
        return list_stage