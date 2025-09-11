from PySide6.QtWidgets import QWizardPage, QVBoxLayout, QListWidget, QListWidgetItem, QCheckBox



class PageProductComponentSelection(QWizardPage):
    def __init__(self, wizard):
        super().__init__()
        self.wizard = wizard
        self.setTitle("Выбор компонентов изделия")
        self.setSubTitle("Отметьте компоненты для задачи")

        layout = QVBoxLayout()
        self.components_list = QListWidget()
        layout.addWidget(self.components_list)
        self.setLayout(layout)

    def initializePage(self):
        self.components_list.clear()
        for comp in self.wizard.product['component']:
            item = QListWidgetItem()
            checkbox = QCheckBox(comp['name'])
            checkbox.setProperty("component", comp)
            item.setSizeHint(checkbox.sizeHint())
            self.components_list.addItem(item)
            self.components_list.setItemWidget(item, checkbox)

    def validatePage(self):
        self.wizard.list_selected_product_component.clear()
        for i in range(self.components_list.count()):
            item = self.components_list.item(i)
            widget = self.components_list.itemWidget(item)
            if isinstance(widget, QCheckBox) and widget.isChecked():
                comp = widget.property("component")
                self.wizard.list_selected_product_component.append(comp)
        return True

    def nextId(self):
        return self.wizard.PAGE_TASK_DETAILS
