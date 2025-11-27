from PySide6.QtWidgets import QWizardPage, QVBoxLayout, QLabel, QComboBox


class PageProfileToolSelection(QWizardPage):
    def __init__(self, wizard):
        super().__init__()
        self.wizard = wizard
        self.setTitle("Выбор инструмента")
        self.setSubTitle("Выберите инструмент для профиля")

        layout = QVBoxLayout()
        self.tool_combo = QComboBox()
        layout.addWidget(QLabel("Инструмент:"))
        layout.addWidget(self.tool_combo)
        self.setLayout(layout)

    def initializePage(self):
        self.tool_combo.clear()
        profile = self.wizard.profile
        for profiletool in profile['profiletool']:
            name = f"Инструмент {profiletool['dimension']['name']}"
            self.tool_combo.addItem(name, profiletool)

    def validatePage(self):
        index = self.tool_combo.currentIndex()
        if index >= 0:
            self.wizard.profiletool = self.tool_combo.itemData(index)
            return True
        return False

    def nextId(self):
        return self.wizard.PAGE_PROFILETOOL_COMPONENT_SELECTION
