"""Страница визарда: выбор компонентов для разработки"""
from PySide6.QtWidgets import QListWidgetItem, QCheckBox


class PageProfiletoolComponentDev:
    """Страница выбора компонентов для разработки"""
    
    def __init__(self, wizard, ui):
        self.wizard = wizard
        self.ui = ui
    
    def load(self):
        """Загрузка компонентов для разработки"""
        self.ui.listWidget_profiletool_component_dev.clear()
        
        if not self.wizard.profileTool:
            return
        
        for component in self.wizard.profileTool['component']:
            item = QListWidgetItem()
            checkbox = QCheckBox(f"{component['type']['name']}")
            checkbox.setProperty("component_id", component['id'])
            self.ui.listWidget_profiletool_component_dev.addItem(item)
            self.ui.listWidget_profiletool_component_dev.setItemWidget(item, checkbox)
    
    def get_selected_component(self):
        """Получение выбранных компонентов"""
        list_selected = []
        for i in range(self.ui.listWidget_profiletool_component_dev.count()):
            item = self.ui.listWidget_profiletool_component_dev.item(i)
            checkbox = self.ui.listWidget_profiletool_component_dev.itemWidget(item)
            if checkbox and checkbox.isChecked():
                component_id = checkbox.property("component_id")
                for comp in self.wizard.profileTool['component']:
                    if comp.get('id') == component_id:
                        list_selected.append(comp)
                        break
        return list_selected
