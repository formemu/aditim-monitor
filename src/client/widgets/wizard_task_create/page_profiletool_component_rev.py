"""Страница визарда: выбор компонентов для изменения"""
from PySide6.QtWidgets import QListWidgetItem, QCheckBox


class PageProfiletoolComponentRev:
    """Страница выбора компонентов для изменения"""
    
    def __init__(self, wizard, ui):
        self.wizard = wizard
        self.ui = ui
    
    def load(self):
        """Загрузка компонентов для изменения"""
        self.ui.listWidget_profiletool_component_rev.clear()
        
        if not self.wizard.profileTool:
            return
        
        for component in self.wizard.profileTool['component']:
            item = QListWidgetItem("")
            checkbox = QCheckBox(f"{component['type']['name']}")
            checkbox.setProperty("component_id", component['id'])
            self.ui.listWidget_profiletool_component_rev.addItem(item)
            self.ui.listWidget_profiletool_component_rev.setItemWidget(item, checkbox)
    
    def get_selected_component(self):
        """Получение выбранных компонентов"""
        list_selected = []
        for i in range(self.ui.listWidget_profiletool_component_rev.count()):
            item = self.ui.listWidget_profiletool_component_rev.item(i)
            checkbox = self.ui.listWidget_profiletool_component_rev.itemWidget(item)
            if checkbox and checkbox.isChecked():
                component_id = checkbox.property("component_id")
                for comp in self.wizard.profileTool['component']:
                    if comp.get('id') == component_id:
                        list_selected.append(comp)
                        break
        return list_selected
