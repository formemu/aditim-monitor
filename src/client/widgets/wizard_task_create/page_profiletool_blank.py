"""Страница визарда: выбор компонентов для заготовок"""
from PySide6.QtWidgets import QListWidgetItem, QCheckBox, QWidget
from .widget_blank_parameter import WidgetBlankParameter


class PageProfiletoolBlank:
    """Страница выбора компонентов для изготовления заготовок"""
    
    def __init__(self, wizard, ui):
        self.wizard = wizard
        self.ui = ui
    
    def load(self):
        """Загрузка компонентов для изготовления заготовок"""
        self.ui.listWidget_profiletool_blank.clear()
        
        # Очищаем контейнер виджетов параметров заготовок
        layout = self.ui.widget_blank_container.layout()
        for child in self.ui.widget_blank_container.findChildren(QWidget):
            child.deleteLater()
        
        if not self.wizard.profileTool:
            return
        
        for component in self.wizard.profileTool['component']:
            item = QListWidgetItem("")
            checkbox = QCheckBox(f"{component['type']['name']}")
            checkbox.setProperty("component_id", component['id'])
            checkbox.toggled.connect(lambda checked, comp=component: 
                                     self.activate_blank_component(checked, comp))
            self.ui.listWidget_profiletool_blank.addItem(item)
            self.ui.listWidget_profiletool_blank.setItemWidget(item, checkbox)
    
    def activate_blank_component(self, checked, component):
        """Добавляет или удаляет виджет параметров заготовки"""
        layout = self.ui.widget_blank_container.layout()
        if checked:
            widget_blank = WidgetBlankParameter(component)
            widget_blank.setProperty("component_id", component['id'])
            layout.addWidget(widget_blank)
        else:
            # Находим и удаляем виджет для этого компонента
            for child in self.ui.widget_blank_container.findChildren(WidgetBlankParameter):
                if child.property("component_id") == component['id']:
                    layout.removeWidget(child)
                    child.deleteLater()
                    break
    
    def get_blank_data_list(self):
        """Получение списка данных заготовок"""
        list_blank_data = []
        for widget_blank in self.ui.widget_blank_container.findChildren(WidgetBlankParameter):
            blank_data = widget_blank.get_blank_data()
            if blank_data:
                list_blank_data.append(blank_data)
        return list_blank_data
