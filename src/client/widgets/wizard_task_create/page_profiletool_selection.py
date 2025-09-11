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
        for pt in profile.get('profile_tool', []):
            name = f"Инструмент {pt['dimension']['name']}"
            self.tool_combo.addItem(name, pt)

    def validatePage(self):
        idx = self.tool_combo.currentIndex()
        if idx >= 0:
            self.wizard.profile_tool = self.tool_combo.itemData(idx)
            return True
        return False

    def nextId(self):
        return self.wizard.PAGE_PROFILE_TOOL_COMPONENT_SELECTION
