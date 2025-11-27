from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QMessageBox, QWizardPage, QVBoxLayout,  QListWidget, QListWidgetItem,
                               QCheckBox, QWidget, QHBoxLayout, QLabel)
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
        if checked:
            widget = WidgetComponent(component)
            self.list_widget.append(widget)
            self.component_to_widget[component['id']] = widget
            self.container_component.layout().addWidget(widget)
        else:
            widget = self.component_to_widget.pop(component['id'], None)
            if widget:
                self.container_component.layout().removeWidget(widget)
                widget.deleteLater()
                if widget in self.list_widget:
                    self.list_widget.remove(widget)

        """Сортирует виджеты по type_id через перестановку в layout"""
        layout = self.container_component.layout()
        dict_widget = []

        # Собираем все виджеты
        for i in range(layout.count()):
            widget = layout.itemAt(i).widget()
            if widget:
                type_id = widget.component.get("type_id")
                dict_widget.append((type_id, widget))

        dict_widget.sort(key=lambda type_id: type_id[0])

        # Переставляем: удаляем все — добавляем заново
        for _, widget in dict_widget:
            layout.removeWidget(widget)
            layout.addWidget(widget)

    def clear_container(self):
        """Очищает контейнер"""
        for child in self.container_component.findChildren(QWidget):
            child.deleteLater()

    def nextId(self):
        return self.wizard.PAGE_TASK_DETAILS

    def get_dict_selected_component(self):
        """Собирает все выбранные компоненты с выбранными этапами и станками"""
        dict_selected_component = []
        for i in range(self.listWidget_component.count()):
            item = self.listWidget_component.item(i)
            checkbox = self.listWidget_component.itemWidget(item)
            if isinstance(checkbox, QCheckBox) and checkbox.isChecked():
                component = checkbox.property("component").copy()
                list_selected_stage = []
                widget = self.component_to_widget.get(component["id"])
                if widget:
                    layout = widget.layout()
                    for j in range(1, layout.count()):  # пропускаем заголовок
                        sublayout = layout.itemAt(j)
                        if not sublayout or not sublayout.layout():
                            continue
                        cb_widget = sublayout.layout().itemAt(0).widget()
                        if isinstance(cb_widget, QCheckBox) and cb_widget.isChecked():
                            stage = cb_widget.property("stage")
                            # Пока без machine — если нет комбобокса
                            list_selected_stage.append({"stage": stage})
                component["list_selected_stage"] = list_selected_stage
                dict_selected_component.append(component)
        return dict_selected_component

    
    def validatePage(self):
        """Проверяет и сохраняет выбранные компоненты в поле wizard'а"""
        self.wizard.dict_selected_profiletool_component = self.get_dict_selected_component()
        if not self.wizard.dict_selected_profiletool_component:
            QMessageBox.warning(self, "Внимание", "Выберите хотя бы один компонент")
            return False
        return True

class WidgetComponent(QWidget):
    def __init__(self, component, parent=None):
        super().__init__(parent)
        self.setLayout(QVBoxLayout())
        self.component = component
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
            self.layout().addLayout(layout)

    def load_stage(self, component):
        profiletool_component_type_id = component['type']['id']
        list_stage = []
        for stage in api_manager.plan['task_component_stage']:
            if stage['profiletool_component_type']['id'] == profiletool_component_type_id:
                list_stage.append(stage)
        list_stage.sort(key=lambda x: x['stage_num'])
        return list_stage