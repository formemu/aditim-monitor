from PySide6.QtWidgets import (QWizardPage, QVBoxLayout, QDateEdit,
                               QLabel, QGroupBox, QTextEdit)
from PySide6.QtCore import QDate


class PageTaskDetails(QWizardPage):
    def __init__(self, wizard):
        super().__init__()
        self.wizard = wizard
        layout = QVBoxLayout()
        group = QGroupBox("Параметры задачи")
        group_layout = QVBoxLayout()
        deadline_layout = QVBoxLayout()
        self.deadline_edit = QDateEdit()
        desc_layout = QVBoxLayout()
        self.description_edit = QTextEdit()

        deadline_layout.addWidget(QLabel("Срок выполнения:"))
        deadline_layout.addWidget(self.deadline_edit)
        group_layout.addLayout(deadline_layout)
        desc_layout.addWidget(QLabel("Описание:"))
        desc_layout.addWidget(self.description_edit)

        layout.addWidget(group)
        group_layout.addLayout(desc_layout)
        group.setLayout(group_layout)
        self.setLayout(layout)

        self.setTitle("Детали задачи")
        self.setSubTitle("Укажите срок и описание")
        self.deadline_edit.setDate(QDate.currentDate().addDays(7))
        self.deadline_edit.setCalendarPopup(True)
        self.description_edit.setMaximumHeight(100)
        
        self.registerField("deadline", self.deadline_edit, "date")
        self.registerField("description", self.description_edit, "plainText")


    def validatePage(self):
        if self.deadline_edit.date().isValid():
            return True
        return False

    def nextId(self):
        return -1