from typing import Dict, Any
from PySide6.QtWidgets import (QCheckBox, QMessageBox, QInputDialog, QListWidgetItem, QDialog, QAbstractItemView)
from PySide6.QtCore import Signal, QSize, Qt, QFile
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QIcon, QKeySequence
from datetime import datetime
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
        
        # Подключаем обработчики для кнопок управления комплектацией
        self.ui.pushButton_product_equipment_add.clicked.connect(self.add_equipment_item)
        self.ui.pushButton_product_equipment_delete.clicked.connect(self.delete_equipment_item)
        self.ui.pushButton_product_equipment_edit.clicked.connect(self.edit_equipment_item)
        
        # Подключаем двойной клик для редактирования
        self.ui.listWidget_product_equipment.itemDoubleClicked.connect(self.edit_equipment_item)
        
        # Включаем перетаскивание для изменения порядка элементов
        self.ui.listWidget_product_equipment.setDragDropMode(QAbstractItemView.InternalMove)
        
        # Устанавливаем обработчик нажатия клавиш для списка оборудования
        self.ui.listWidget_product_equipment.keyPressEvent = self.equipment_list_key_press_event

        # Set icons for buttons
        button = self.ui.pushButton_product_equipment_add
        button.setIcon(QIcon(ICON_PATHS["ADD"]))
        button.setIconSize(QSize(24, 24))
        button.setToolTip("Добавить оборудование")

        button = self.ui.pushButton_product_equipment_delete
        button.setIcon(QIcon(ICON_PATHS["DELETE"]))
        button.setIconSize(QSize(24, 24))
        button.setToolTip("Удалить выбранное оборудование (Delete)")

        button = self.ui.pushButton_product_equipment_edit
        button.setIcon(QIcon(ICON_PATHS["EDIT"]))
        button.setIconSize(QSize(24, 24))
        button.setToolTip("Изменить выбранное оборудование (двойной клик)")

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
        # Проверка артикула профиля
        profile_article = self.ui.lineEdit_profile_article.text().strip()
        if not profile_article:
            raise ValueError("Введите артикул профиля")
        
        # Проверка выбора департамента
        if self.ui.comboBox_product_departament.currentData() is None:
            raise ValueError("Выберите департамент")
            
        selected_equipment = []
        for checkbox in self.ui.widget_profile_equipment_choice.findChildren(QCheckBox):
            if checkbox.isChecked():
                selected_equipment.append(checkbox.text())

        if not selected_equipment:
            raise ValueError("Выберите хотя бы одно оборудование")

        return {
            "id_profile": profile_article,  # Оставляем как строку для поиска профиля
            "id_departament": self.ui.comboBox_product_departament.currentData(),
            "equipment": ", ".join(selected_equipment),
            "deadline": self.ui.dateEdit_profile_mfdate.date().toString("yyyy-MM-dd") + "T00:00:00",
            "position": 999,
            "id_type_work": 1,
            "id_status": 1
        }

    def create_product_task(self) -> Dict[str, Any]:
        # Проверка имени продукта
        product_name = self.ui.lineEdit_product_name.text().strip()
        if not product_name:
            raise ValueError("Введите название продукта")
        
        # Проверка выбора департамента
        if self.ui.comboBox_product_departament.currentData() is None:
            raise ValueError("Выберите департамент")
        
        # Проверка типа работы
        if self.ui.comboBox_product_type_work.currentData() is None:
            raise ValueError("Выберите тип работы")
            
        equipment_items = []
        for i in range(self.ui.listWidget_product_equipment.count()):
            item_text = self.ui.listWidget_product_equipment.item(i).text().strip()
            if item_text:  # Добавляем только непустые элементы
                equipment_items.append(item_text)

        if not equipment_items:
            raise ValueError("Добавьте хотя бы одно оборудование")

        return {
            "id_product": product_name,
            "id_departament": self.ui.comboBox_product_departament.currentData(),
            "equipment": ", ".join(equipment_items),
            "deadline": self.ui.dateEdit_product_mfdate.date().toString("yyyy-MM-dd") + "T00:00:00",
            "position": 999,
            "id_type_work": self.ui.comboBox_product_type_work.currentData(),
            "id_status": 1
        }

    def add_equipment_item(self):
        """Добавить элемент оборудования в список"""
        text, ok = QInputDialog.getText(
            self, 
            "Добавить оборудование", 
            "Введите название оборудования:",
            text=""
        )
        
        if ok and text.strip():
            # Проверяем, что такого элемента еще нет в списке
            existing_items = []
            for i in range(self.ui.listWidget_product_equipment.count()):
                existing_items.append(self.ui.listWidget_product_equipment.item(i).text())
            
            if text.strip() not in existing_items:
                item = QListWidgetItem(text.strip())
                self.ui.listWidget_product_equipment.addItem(item)
            else:
                QMessageBox.warning(
                    self, 
                    "Предупреждение", 
                    "Такое оборудование уже добавлено в список!"
                )

    def delete_equipment_item(self):
        """Удалить выбранный элемент оборудования из списка"""
        current_row = self.ui.listWidget_product_equipment.currentRow()
        
        if current_row >= 0:
            item = self.ui.listWidget_product_equipment.item(current_row)
            reply = QMessageBox.question(
                self,
                "Подтверждение",
                f"Удалить оборудование '{item.text()}'?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.ui.listWidget_product_equipment.takeItem(current_row)
        else:
            QMessageBox.information(
                self,
                "Информация",
                "Выберите элемент для удаления"
            )

    def edit_equipment_item(self):
        """Изменить выбранный элемент оборудования"""
        current_row = self.ui.listWidget_product_equipment.currentRow()
        
        if current_row >= 0:
            item = self.ui.listWidget_product_equipment.item(current_row)
            current_text = item.text()
            
            text, ok = QInputDialog.getText(
                self,
                "Изменить оборудование",
                "Введите новое название оборудования:",
                text=current_text
            )
            
            if ok and text.strip():
                # Проверяем, что такого элемента еще нет в списке (кроме текущего)
                existing_items = []
                for i in range(self.ui.listWidget_product_equipment.count()):
                    if i != current_row:
                        existing_items.append(self.ui.listWidget_product_equipment.item(i).text())
                
                if text.strip() not in existing_items:
                    item.setText(text.strip())
                else:
                    QMessageBox.warning(
                        self,
                        "Предупреждение",
                        "Такое оборудование уже есть в списке!"
                    )
        else:
            QMessageBox.information(
                self,
                "Информация", 
                "Выберите элемент для изменения"
            )

    def equipment_list_key_press_event(self, event):
        """Обработчик нажатий клавиш для списка оборудования"""
        if event.key() == Qt.Key_Delete:
            self.delete_equipment_item()
        else:
            # Вызываем стандартный обработчик для других клавиш
            super(type(self.ui.listWidget_product_equipment), self.ui.listWidget_product_equipment).keyPressEvent(event)
