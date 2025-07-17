import os
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QListWidget, QListWidgetItem, QPushButton, QHBoxLayout, QMessageBox
from PySide6.QtCore import Qt
from server_api import ServerAPI

class StatusDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Выбор статуса задачи")
        self.setMinimumSize(300, 200)

        layout = QVBoxLayout(self)

        label = QLabel("Выберите статус для задачи:")
        layout.addWidget(label)

        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)

        btn_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("Отмена")
        self.cancel_button.clicked.connect(self.reject)
        btn_layout.addWidget(self.ok_button)
        btn_layout.addWidget(self.cancel_button)

        layout.addLayout(btn_layout)

        self.load_statuses()

    def load_statuses(self):
        try:
            statuses = ServerAPI.get_statuses()
            self.list_widget.clear()
            for status in statuses:
                item = QListWidgetItem(status['name'])
                item.setData(Qt.UserRole, status['id'])
                self.list_widget.addItem(item)
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить статусы: {e}")

    def get_selected_status(self):
        selected_items = self.list_widget.selectedItems()
        if selected_items:
            item = selected_items[0]
            name = item.text()
            status_id = item.data(Qt.UserRole)
            return name, status_id
        return None, None
