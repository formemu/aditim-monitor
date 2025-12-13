"""Страница визарда: выбор инструмента профиля"""
from PySide6.QtWidgets import QWizardPage, QListWidgetItem
from PySide6.QtCore import Qt


class PageProfiletoolSelection:
    """Страница выбора инструмента профиля"""
    
    def __init__(self, wizard, ui):
        self.wizard = wizard
        self.ui = ui
        self.setup_page()
    
    def setup_page(self):
        """Настройка страницы"""
        # Сигналы поиска
        self.ui.lineEdit_profile_search.textChanged.connect(self.on_search_profile)
        self.ui.lineEdit_profile_search.returnPressed.connect(self.on_profile_selected)
        
        # Выбор из результатов
        self.ui.listWidget_profile_search.itemSelectionChanged.connect(self.on_profile_selected)
        self.ui.listWidget_profile_search.itemClicked.connect(lambda _: self.on_profile_selected())
        
        # Выбор размерности
        self.ui.comboBox_dimension.currentIndexChanged.connect(self.on_dimension_selected)
    
    def on_search_profile(self, text: str):
        """Поиск профиля по артиклу"""
        from ...api_manager import api_manager
        
        self.ui.listWidget_profile_search.clear()
        for profile in api_manager.search_in('profile', 'article', text)[:10]:
            item = QListWidgetItem(f"{profile['article']}")
            item.setData(Qt.UserRole, profile)
            self.ui.listWidget_profile_search.addItem(item)
    
    def on_profile_selected(self):
        """Обработка выбора профиля"""
        item = self.ui.listWidget_profile_search.currentItem()
        if not item:
            return
        
        self.wizard.task_data["profile"] = item.data(Qt.UserRole)
        self.ui.lineEdit_profile_search.setText(f"{self.wizard.task_data['profile']['article']}")
        
        # Загрузка размерностей
        self.ui.comboBox_dimension.clear()
        for profiletool in self.wizard.task_data["profile"]['profiletool']:
            name = profiletool['dimension']['name']
            self.ui.comboBox_dimension.addItem(name, profiletool)
    
    def on_dimension_selected(self):
        """Обработка выбора размерности"""
        if self.ui.comboBox_dimension.currentIndex() == -1:
            self.wizard.profileTool = None
        else:
            self.wizard.profileTool = self.ui.comboBox_dimension.currentData()
            self.wizard.task_data["profiletool_id"] = self.wizard.profileTool['id']
