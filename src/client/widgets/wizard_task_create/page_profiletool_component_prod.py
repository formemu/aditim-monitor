"""Страница визарда: выбор компонентов для производства"""
from PySide6.QtWidgets import QListWidgetItem, QCheckBox, QWidget
from PySide6.QtCore import Qt
from .widget_profiletool_component_stage import WidgetProfiletoolComponentStage


class PageProfiletoolComponentProd:
    """Страница выбора компонентов для производства"""
    
    def __init__(self, wizard, ui):
        self.wizard = wizard
        self.ui = ui
    
    def load(self):
        """Загрузка компонентов для производства"""
        self.ui.listWidget_profiletool_component_prod.clear()
        
        # Очищаем контейнер виджетов
        for child in self.ui.widget_profiletool_component_container.findChildren(QWidget):
            child.deleteLater()
        
        if not self.wizard.profileTool:
            return
        
        for component in self.wizard.profileTool['component']:
            component.setdefault('stage', [])
            item = QListWidgetItem("")
            item.setData(Qt.UserRole, component)
            self.ui.listWidget_profiletool_component_prod.addItem(item)
            
            checkbox = QCheckBox(f"{component['type']['name']}")
            checkbox.setProperty("component_id", component['id'])
            checkbox.toggled.connect(lambda checked, comp=component: 
                                     self.activate_component(checked, comp))
            self.ui.listWidget_profiletool_component_prod.setItemWidget(item, checkbox)
    
    def activate_component(self, checked, component):
        """Активация/деактивация виджета компонента"""
        layout = self.ui.widget_profiletool_component_container.layout()
        if checked:
            widget_component = WidgetProfiletoolComponentStage(component)
            layout.addWidget(widget_component)
        else:
            # Находим и удаляем виджет
            for child in self.ui.widget_profiletool_component_container.findChildren(WidgetProfiletoolComponentStage):
                if child.component.get('id') == component.get('id'):
                    layout.removeWidget(child)
                    child.deleteLater()
                    break
    
    def get_selected_component(self):
        """Получение выбранных компонентов"""
        list_selected = []
        for i in range(self.ui.listWidget_profiletool_component_prod.count()):
            item = self.ui.listWidget_profiletool_component_prod.item(i)
            checkbox = self.ui.listWidget_profiletool_component_prod.itemWidget(item)
            if checkbox and checkbox.isChecked():
                component_id = checkbox.property("component_id")
                for comp in self.wizard.profileTool['component']:
                    if comp.get('id') == component_id:
                        list_selected.append(comp)
                        break
        return list_selected
