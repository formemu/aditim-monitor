from PySide6.QtWidgets import (QWizardPage, QVBoxLayout, QDateEdit,
                               QLabel, QGroupBox, QTextEdit)
from PySide6.QtCore import QDate


class PageTaskDetails(QWizardPage):
    def __init__(self, wizard):
        super().__init__()
        self.wizard = wizard
        self.setTitle("Детали задачи")
        self.setSubTitle("Укажите срок и описание")

        layout = QVBoxLayout()

        # Группа для дедлайна и описания
        group = QGroupBox("Параметры задачи")
        group_layout = QVBoxLayout()

        # Дедлайн
        deadline_layout = QVBoxLayout()
        deadline_layout.addWidget(QLabel("Срок выполнения:"))
        self.deadline_edit = QDateEdit()
        self.deadline_edit.setDate(QDate.currentDate().addDays(7))
        self.deadline_edit.setCalendarPopup(True)
        deadline_layout.addWidget(self.deadline_edit)
        group_layout.addLayout(deadline_layout)

        # Описание
        desc_layout = QVBoxLayout()
        desc_layout.addWidget(QLabel("Описание:"))
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(100)
        desc_layout.addWidget(self.description_edit)
        group_layout.addLayout(desc_layout)

        self.registerField("deadline", self.deadline_edit, "date")
        self.registerField("description", self.description_edit, "plainText")
        group.setLayout(group_layout)
        layout.addWidget(group)
        self.setLayout(layout)

    def validatePage(self):
        if self.deadline_edit.date().isValid():
            return True
        return False

    def nextId(self):
        return -1