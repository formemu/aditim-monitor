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
        for profile_tool in profile['profile_tool']:
            name = f"Инструмент {profile_tool['dimension']['name']}"
            self.tool_combo.addItem(name, profile_tool)

    def validatePage(self):
        index = self.tool_combo.currentIndex()
        if index >= 0:
            self.wizard.profile_tool = self.tool_combo.itemData(index)
            return True
        return False

    def nextId(self):
        return self.wizard.PAGE_PROFILE_TOOL_COMPONENT_SELECTION
