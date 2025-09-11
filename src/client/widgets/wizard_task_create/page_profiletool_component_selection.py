from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QWizardPage, QVBoxLayout, QLabel, QListWidget,
                               QListWidgetItem, QCheckBox, QWidget, 
                               QHBoxLayout, QGridLayout, QSpacerItem, QSizePolicy)
from ...api_manager import api_manager



class PageProfileToolComponentSelection(QWizardPage):
    def __init__(self, wizard):
        super().__init__()
        self.wizard = wizard
        self.setTitle("Выбор компонентов")
        self.setSubTitle("Отметьте компоненты, которые нужно изготовить")

        # Основной макет
        main_layout = QHBoxLayout()
        self.setLayout(main_layout)

        # Слева — список компонентов
        self.list_component = QListWidget()
        self.list_component.setMaximumWidth(300)
        main_layout.addWidget(self.list_component)

        # Справа — контейнер для сетки
        self.grid_container = QWidget()
        self.grid_layout = QGridLayout(self.grid_container)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.grid_layout.setSpacing(10)
        main_layout.addWidget(self.grid_container)

        # Храним: comp → widget
        self.component_to_widget = {}
        self.list_widget = []
        self.max_column = 3

    def initializePage(self):
        self.list_component.clear()
        self.clear_grid()
        self.component_to_widget.clear()
        self.list_widget.clear()

        tool = self.wizard.profile_tool
        for component in tool['component']:
            item = QListWidgetItem(self.list_component)
            checkbox = QCheckBox(f"{component['type']['name']}")
            checkbox.setProperty("component", component)
            checkbox.toggled.connect(lambda checked, c=component, cb=checkbox: self.on_component_toggled(checked, c, cb))
            self.list_component.setItemWidget(item, checkbox)

    def on_component_toggled(self, checked, component, checkbox):
        if checked:
            widget = self.create_component_widget(component)
            self.list_widget.append(widget)
            self.component_to_widget[component['id']] = widget
            self.rebuild_grid()
        else:
            widget = self.component_to_widget.pop(component['id'], None)
            if widget and widget in self.list_widget:
                self.list_widget.remove(widget)
            self.rebuild_grid()

    def create_component_widget(self, component):
        widget = QWidget()
        widget.setFixedSize(180, 200)
        widget.setStyleSheet("border:1px solid #b3d9ff; padding:5px;")

        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)

        # Заголовок
        title = QLabel(f"<b>{component['type']['name']}</b>")
        title.setStyleSheet("font-size: 10pt;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Загружаем операции, отфильтрованные по типу
        list_stage = self.load_stage(component)
        for stage in list_stage:
            cb = QCheckBox(f"{stage['num_stage']}. {stage['name']}")
            cb.setProperty("stage", stage)
            layout.addWidget(cb)

        return widget

    def load_stage(self, component):
        """
        Загружает операции из api_manager.plan_task_component_stage,
        фильтруя по component_type_id == component['type']['id']
        """
        component_type_id = component['type']['id']
        list_stage = []

        for item in api_manager.plan_task_component_stage:
            if item['component_type']['id'] == component_type_id:
                stage = item['task_component_stage']
                list_stage.append({
                    "name": stage['name'],
                    "id": stage['id'],
                    "num_stage": item['num_stage'],
                    "description": stage.get('description', '')
                })

        # Сортируем по num_stage
        list_stage.sort(key=lambda x: x['num_stage'])

        return list_stage

    def rebuild_grid(self):
        """Перестраивает сетку: 3 виджета в ряду, прижаты к верху и слева"""
        self.clear_grid()
        if not self.list_widget:
            return

        # Добавляем виджеты
        for i, widget in enumerate(self.list_widget):
            row = i // self.max_column
            col = i % self.max_column
            self.grid_layout.addWidget(widget, row, col)

        # Добавляем растягиваемый спейсер в правый нижний угол
        # Он займёт всё оставшееся пространство и "прижмёт" виджеты влево-вверх
        last_row = (len(self.list_widget) - 1) // self.max_column + 1
        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.grid_layout.addItem(spacer, last_row, 0, 1, self.max_column)

    def clear_grid(self):
        """Очищает сетку"""
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)

    def validatePage(self):
        self.wizard.list_selected_profile_tool_component.clear()
        for i in range(self.list_component.count()):
            item = self.list_component.item(i)
            checkbox = self.list_component.itemWidget(item)
            if isinstance(checkbox, QCheckBox) and checkbox.isChecked():
                component = checkbox.property("component")
                comp_id = component['id']

                # Сохраняем выбранные операции
                widget = self.component_to_widget.get(comp_id)
                selected_stage = []
                if widget:
                    layout = widget.layout()
                    for j in range(1, layout.count()):  # пропускаем заголовок
                        cb = layout.itemAt(j).widget()
                        if isinstance(cb, QCheckBox) and cb.isChecked():
                            selected_stage.append(cb.property("stage"))
                component['list_selected_stage'] = selected_stage
                self.wizard.list_selected_profile_tool_component.append(component)
        return len(self.wizard.list_selected_profile_tool_component) > 0

    def nextId(self):
        return self.wizard.PAGE_TASK_DETAILS
