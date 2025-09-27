from PySide6.QtCore import  Qt
from PySide6.QtWidgets import QWizardPage, QVBoxLayout, QLabel, QLineEdit, QListWidget, QListWidgetItem, QComboBox
from ...api_manager import api_manager



class PageProfileSelection(QWizardPage):    
    def __init__(self, wizard):
        super().__init__()
        self.wizard = wizard
        layout = QVBoxLayout()
        self.lineEdit_search = QLineEdit()
        self.listWidget_result = QListWidget()
        self.comboBox_type = QComboBox()

        self.registerField("type_id", self.comboBox_type , "currentData")
        
        self.setTitle("Выбор профиля")
        self.setSubTitle("Введите артикул или описание")
        self.lineEdit_search.setPlaceholderText("Поиск профиля...")
        layout.addWidget(QLabel("Поиск:"))
        layout.addWidget(self.lineEdit_search)
        layout.addWidget(self.listWidget_result)
        layout.addWidget(QLabel("Тип задачи:"))
        layout.addWidget(self.comboBox_type)   
        self.setLayout(layout)

        self.lineEdit_search.textChanged.connect(self.on_search)

        

    def on_search(self, text):
        self.listWidget_result.clear()
        if not text.strip():
            return
        results = api_manager.search_in('profile', 'article', text)[:10]
        for profile in results:
            item = QListWidgetItem(f"{profile['article']}")
            item.setData(Qt.UserRole, profile)
            self.listWidget_result.addItem(item)
  

    def initializePage(self):
        self.listWidget_result.clear()
        self.fill_type_combo()

    def fill_type_combo(self):
        self.comboBox_type.clear()
        types = api_manager.directory['task_type']
        for task_type in types:
            self.comboBox_type.addItem(task_type['name'], task_type['id'])

        

    def validatePage(self):
        current_item = self.listWidget_result.currentItem()
        if current_item:
            profile = current_item.data(Qt.UserRole)
            self.wizard.profile = profile
            return True
        return False

    def nextId(self):
        return self.wizard.PAGE_PROFILETOOL_SELECTION
