from PySide6.QtWidgets import QWizardPage, QVBoxLayout, QLabel,  QComboBox


class PageStart(QWizardPage):
    def __init__(self, wizard):
        super().__init__()
        self.wizard = wizard
        self.setTitle("Тип задачи")
        self.setSubTitle("Выберите, для чего создается задача")

        layout = QVBoxLayout()
        self.task_type_combo = QComboBox()
        self.task_type_combo.addItems([
            "Задача для инструмента профиля",
            "Задача для изделия"
        ])
        layout.addWidget(QLabel("Тип задачи:"))
        layout.addWidget(self.task_type_combo)
        self.setLayout(layout)

    def nextId(self):
        selected = self.task_type_combo.currentIndex()
        if selected == 0:
            return self.wizard.PAGE_PROFILE_SELECTION
        else:
            return self.wizard.PAGE_PRODUCT_SELECTION