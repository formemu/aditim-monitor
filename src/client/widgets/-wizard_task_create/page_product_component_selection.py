from PySide6.QtWidgets import QWizardPage, QVBoxLayout, QListWidget, QListWidgetItem, QCheckBox



class PageProductComponentSelection(QWizardPage):
    def __init__(self, wizard):
        super().__init__()
        self.wizard = wizard
        self.setTitle("Выбор компонентов изделия")
        self.setSubTitle("Отметьте компоненты для задачи")

        layout = QVBoxLayout()
        self.list_component = QListWidget()
        layout.addWidget(self.list_component)
        self.setLayout(layout)

    def initializePage(self):
        self.list_component.clear()
        for comp in self.wizard.product['component']:
            item = QListWidgetItem()
            checkbox = QCheckBox(comp['name'])
            checkbox.setProperty("component", comp)
            item.setSizeHint(checkbox.sizeHint())
            self.list_component.addItem(item)
            self.list_component.setItemWidget(item, checkbox)

    def validatePage(self):
        self.wizard.dict_selected_product_component.clear()
        for i in range(self.list_component.count()):
            item = self.list_component.item(i)
            widget = self.list_component.itemWidget(item)
            if isinstance(widget, QCheckBox) and widget.isChecked():
                comp = widget.property("component")
                self.wizard.dict_selected_product_component.append(comp)
        return True

    def nextId(self):
        return self.wizard.PAGE_TASK_DETAILS
