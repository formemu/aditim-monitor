from typing import Dict, Any
from PySide6.QtWidgets import ( QCheckBox , QMessageBox)
from PySide6.QtCore import Signal, QSize, QSize
from PySide6.QtWidgets import QDialog
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile
from PySide6.QtGui import QIcon
import os
from ..style_utils import load_styles_with_constants
from ..constants import PATHS
from ..resources import ICON_PATHS 

class DialogTask(QDialog):
    task_created = Signal(dict)

    def __init__(self, api_client, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.departments = []
        self.profiles = []
        self.products = []
        self.type_works = []

        # Load the UI file
        ui_file = QFile(PATHS["DIALOG_TASK_UI"])
        ui_file.open(QFile.ReadOnly)
        loader = QUiLoader()
        self.ui = loader.load(ui_file, self)
        ui_file.close()

        # Replace layout
        self.setLayout(self.ui.layout())

        # Apply styles
        self.apply_styles()

        self.setup_logic()
        self.load_data()

    def apply_styles(self):
        try:
            stylesheet = load_styles_with_constants("src/client/resources/styles/dialogs_template.qss")
            self.setStyleSheet(stylesheet)
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить стили: {e}")

    def setup_logic(self):
        self.ui.buttonBox.accepted.connect(self.create_task)
        self.ui.buttonBox.rejected.connect(self.reject)

        # Set icons for buttons
        button = self.ui.pushButton_product_equipment_add
        button.setIcon(QIcon(ICON_PATHS["ADD"]))
        button.setIconSize(QSize(24, 24))

        button = self.ui.pushButton_product_equipment_delete
        button.setIcon(QIcon(ICON_PATHS["DELETE"]))
        button.setIconSize(QSize(24, 24))

        button = self.ui.pushButton_product_equipment_edit
        button.setIcon(QIcon(ICON_PATHS["EDIT"]))
        button.setIconSize(QSize(24, 24))

    def load_data(self):
        try:
            self.departments = self.api_client.get_departments()
            for dept in self.departments:
                self.ui.comboBox_product_departament.addItem(dept["name"], dept["id"])

            self.type_works = self.api_client.get_type_works()
            for work_type in self.type_works:
                self.ui.comboBox_product_type_work.addItem(work_type["name"], work_type["id"])

            self.profiles = self.api_client.get_profiles()
            for profile in self.profiles:
                self.ui.lineEdit_profile_article.setText(profile["article"])

            self.products = self.api_client.get_products()
            for product in self.products:
                self.ui.lineEdit_product_name.setText(product["name"])

        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить данные: {e}")

    def create_task(self):
        try:
            current_tab = self.ui.tabWidget.currentIndex()
            if current_tab == 0:
                task_data = self.create_profile_task()
            else:
                task_data = self.create_product_task()

            result = self.api_client.create_task(task_data)
            QMessageBox.information(self, "Успех", "Задача создана успешно!")
            self.task_created.emit(task_data)
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось создать задачу: {e}")

    def create_profile_task(self) -> Dict[str, Any]:
        selected_equipment = []
        for checkbox in self.ui.widget_profile_equipment_choice.findChildren(QCheckBox):
            if checkbox.isChecked():
                selected_equipment.append(checkbox.text())

        if not selected_equipment:
            raise ValueError("Выберите хотя бы одно оборудование")

        return {
            "id_profile": self.ui.lineEdit_profile_article.text(),
            "id_departament": self.ui.comboBox_product_departament.currentData(),
            "equipment": ", ".join(selected_equipment),
            "deadline": self.ui.dateEdit_profile_mfdate.date().toString("yyyy-MM-dd"),
            "position": 999,
            "id_type_work": 1,
            "id_status": 1
        }

    def create_product_task(self) -> Dict[str, Any]:
        equipment_items = []
        for i in range(self.ui.listWidget_product_equipment.count()):
            equipment_items.append(self.ui.listWidget_product_equipment.item(i).text())

        if not equipment_items:
            raise ValueError("Добавьте хотя бы одно оборудование")

        return {
            "id_product": self.ui.lineEdit_product_name.text(),
            "id_departament": self.ui.comboBox_product_departament.currentData(),
            "equipment": ", ".join(equipment_items),
            "deadline": self.ui.dateEdit_product_mfdate.date().toString("yyyy-MM-dd"),
            "position": 999,
            "id_type_work": self.ui.comboBox_product_type_work.currentData(),
            "id_status": 1
        }
