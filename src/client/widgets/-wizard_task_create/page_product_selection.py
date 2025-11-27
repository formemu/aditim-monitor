from PySide6.QtCore import  Qt
from PySide6.QtWidgets import QWizardPage, QVBoxLayout, QLabel, QLineEdit, QListWidget, QListWidgetItem
from ...api_manager import api_manager



class PageProductSelection(QWizardPage):
    def __init__(self, wizard):
        super().__init__()
        self.wizard = wizard
        self.setTitle("Выбор изделия")
        self.setSubTitle("Введите название или описание")

        layout = QVBoxLayout()
        self.search_edit = QLineEdit()
        self.results_list = QListWidget()

        layout.addWidget(QLabel("Поиск:"))
        layout.addWidget(self.search_edit)
        layout.addWidget(self.results_list)
        self.setLayout(layout)

        self.search_edit.textChanged.connect(self.on_search)

    def on_search(self, text):
        self.results_list.clear()
        if not text.strip():
            return
        results = api_manager.search_in('product', 'name', text)[:10]
        for product in results:
            item = QListWidgetItem(f"{product['name']} - {product['description']}")
            item.setData(Qt.UserRole, product)
            self.results_list.addItem(item)

    def validatePage(self):
        item = self.results_list.currentItem()
        if item:
            self.wizard.product = item.data(Qt.UserRole)
            return True
        return False

    def nextId(self):
        return self.wizard.PAGE_PRODUCT_COMPONENT_SELECTION
