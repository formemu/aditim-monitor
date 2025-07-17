from PySide6.QtWidgets import QWidget, QLabel, QSizePolicy
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile
import os

UI_PATH = os.path.join(os.path.dirname(__file__), "form_item_queue.ui")


class FormItemQueue(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        loader = QUiLoader()
        ui_file = QFile(UI_PATH)
        ui_file.open(QFile.ReadOnly)
        self.ui = loader.load(ui_file, self)
        ui_file.close()
        self.setLayout(self.ui.layout())
        self.task_id = None  # Добавлено поле для хранения id задачи
        # Стилизация карточки
        self.setMinimumHeight(100)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.setStyleSheet('''
            QWidget#FormItemQueue {
                background: transparent;
                border-radius: 12px;
                border: none;
                margin: 0px;
                padding: 0px;
            }
            QWidget#widget_queue_body {
                background-color: #23262B;
                border-radius: 12px;
                border: 1px solid #555;
                margin: 0px;
                padding: 0px;
            }
            QLabel {
                color: #fff;
                font-size: 15px;
            }
            QLabel#label_type_product {
                color: #E53935;
                font-size: 17px;
                font-weight: 600;
            }
            QLabel#label_departament {
                color: #1976D2;
                font-size: 15px;
                font-weight: 600;
            }
            QLabel#label_type_product_header, QLabel#label_stage_header, QLabel#label_equipment_header, QLabel#label_departament_header, QLabel#label_deadline_header, QLabel#label_type_work_header {
                color: #B0B8C1;
                font-size: 13px;
            }
        ''')

    def set_data(self, task):
        self.task_id = task.get("id")  # Сохраняем id задачи
        label_type_product = self.findChild(QLabel, "label_type_product")
        name = task.get("name")
        if not name:
            # fallback: task_type или id
            name = task.get("task_type", "Без названия")
        if label_type_product:
            label_type_product.setObjectName("label_type_product")
            label_type_product.setText(str(name))
        else:
            print("label_type_product not found")
        label_stage = self.findChild(QLabel, "label_stage")
        if label_stage:
            label_stage.setText(str(task.get("stage", "")))
        else:
            print("label_stage not found")
        label_equipment = self.findChild(QLabel, "label_equipment")
        if label_equipment:
            label_equipment.setText(str(task.get("equipment", "")))
        else:
            print("label_equipment not found")
        label_departament = self.findChild(QLabel, "label_departament")
        if label_departament:
            label_departament.setObjectName("label_departament")
            label_departament.setText(str(task.get("departament", "")))
        else:
            print("label_departament not found")
        label_deadline = self.findChild(QLabel, "label_deadline")
        if label_deadline:
            label_deadline.setText(str(task.get("deadline", "")))
        else:
            print("label_deadline not found")
        label_type_work = self.findChild(QLabel, "label_type_work")
        if label_type_work:
            label_type_work.setText(str(task.get("type_work", "")))
        else:
            print("label_type_work not found")
