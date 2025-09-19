from PySide6.QtCore import  Qt
from PySide6.QtWidgets import QWizardPage, QVBoxLayout, QLabel, QLineEdit, QListWidget, QListWidgetItem, QComboBox
from ...api_manager import api_manager



class PageProfileSelection(QWizardPage):    
    def __init__(self, wizard):
        super().__init__()
        self.wizard = wizard
        self.setTitle("Выбор профиля")
        self.setSubTitle("Введите артикул или описание")

        layout = QVBoxLayout()
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Поиск профиля...")
        self.results_list = QListWidget()
        self.type_combo = QComboBox()


        layout.addWidget(QLabel("Поиск:"))
        layout.addWidget(self.search_edit)
        layout.addWidget(self.results_list)
        layout.addWidget(QLabel("Тип задачи:"))
        layout.addWidget(self.type_combo)   
        self.setLayout(layout)

        self.search_edit.textChanged.connect(self.on_search)

    def on_search(self, text):
        self.results_list.clear()
        if not text.strip():
            return
        results = api_manager.search_in('profile', 'article', text)[:10]
        for profile in results:
            item = QListWidgetItem(f"{profile['article']}")
            item.setData(Qt.UserRole, profile)
            self.results_list.addItem(item)
  

    def initializePage(self):
        self.results_list.clear()
        self.fill_type_combo()

    def fill_type_combo(self):
        self.type_combo.clear()
        types = api_manager.directory['task_type']
        for task_type in types:
            self.type_combo.addItem(task_type['name'], task_type['id'])

        self.registerField("type_id", self.type_combo , "currentData")

    def validatePage(self):
        current_item = self.results_list.currentItem()
        if current_item:
            profile = current_item.data(Qt.UserRole)
            self.wizard.profile = profile
            return True
        return False

    def nextId(self):
        return self.wizard.PAGE_PROFILE_TOOL_SELECTION
