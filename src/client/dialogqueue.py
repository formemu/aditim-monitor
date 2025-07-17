import os
import httpx
from PySide6.QtWidgets import QDialog, QMessageBox, QInputDialog
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile
from server_api import ServerAPI

class DialogQueue(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        loader = QUiLoader()
        ui_file = QFile(os.path.join(os.path.dirname(__file__), "dialogqueue.ui"))
        ui_file.open(QFile.ReadOnly)
        self.ui = loader.load(ui_file, self)
        ui_file.close()
        self.setLayout(self.ui.layout())
        self.setWindowTitle(self.ui.windowTitle())
        # --- Кнопки ---
        self.ui.buttonBox.accepted.connect(self.accept)
        self.ui.buttonBox.rejected.connect(self.reject)

        # --- Комплектация product ---
        self.ui.pushButton_product_equipment_add.clicked.connect(self.add_product_equipment)
        self.ui.pushButton_product_equipment_delete.clicked.connect(self.delete_product_equipment)
        # --- Динамическое заполнение департаментов и типа работ ---
        self.fill_departaments()
        self.fill_type_works()
    def fill_type_works(self):
        try:
            resp = httpx.get("http://localhost:8000/type_works")
            if resp.status_code == 200:
                type_works = resp.json()
                self.ui.comboBox_product_type_work.clear()
                for tw in type_works:
                    self.ui.comboBox_product_type_work.addItem(tw["name"], tw["id"])
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить типы работ: {e}")
        # --- Валидация ---
        self.valid = False

    def fill_departaments(self):
        try:
            departs = ServerAPI.get_departaments()
            self.ui.comboBox_product_departament.clear()
            for d in departs:
                self.ui.comboBox_product_departament.addItem(d["name"], d["id"])
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить департаменты: {e}")

    def add_product_equipment(self):
        text, ok = QInputDialog.getText(self, "Добавить компонент", "Название компонента:")
        if ok and text:
            self.ui.listWidget_product_equipment.addItem(text)

    def delete_product_equipment(self):
        row = self.ui.listWidget_product_equipment.currentRow()
        if row >= 0:
            self.ui.listWidget_product_equipment.takeItem(row)

    def get_data(self):
        tab = self.ui.tabWidget.currentIndex()
        if tab == 0:
            # Профиль
            article = self.ui.lineEdit_profile_article.text().strip()
            mfdate = self.ui.dateEdit_profile_mfdate.date().toString("yyyy-MM-dd")
            # Тип работы
            type_work = None
            for btn in [self.ui.radioButton_profile_works_new, self.ui.radioButton_profile_works_new_variant,
                        self.ui.radioButton_profile_works_add_to, self.ui.radioButton_profile_works_remake,
                        self.ui.radioButton_profile_works_revision]:
                if btn.isChecked():
                    type_work = btn.text()
            # Комплектация (checkbox)
            equipment = []
            for cb in [self.ui.checkBox_profile_equipment_pl1, self.ui.checkBox_profile_equipmen_pl2,
                       self.ui.checkBox_profile_equipment_pl3, self.ui.checkBox_profile_equipment_pl4,
                       self.ui.checkBox_profile_equipment_kernel, self.ui.checkBox_profile_equipment_averager,
                       self.ui.checkBox_profile_equipment_conductor]:
                if cb.isChecked():
                    equipment.append(cb.text())
            return {
                "tab": "profile",
                "article": article,
                "mfdate": mfdate,
                "type_work": type_work,
                "equipment": equipment
            }
        else:
            # Продукт
            name = self.ui.lineEdit_product_name.text().strip()
            departament = self.ui.comboBox_product_departament.currentText()
            mfdate = self.ui.dateEdit_product_mfdate.date().toString("yyyy-MM-dd")
            equipment = [self.ui.listWidget_product_equipment.item(i).text() for i in range(self.ui.listWidget_product_equipment.count())]
            # Получаем id выбранного типа работы
            type_work_id = self.ui.comboBox_product_type_work.currentData()
            return {
                "tab": "product",
                "name": name,
                "departament": departament,
                "mfdate": mfdate,
                "equipment": equipment,
                "id_type_work": type_work_id
            }

    def validate(self):
        data = self.get_data()
        if data["tab"] == "profile":
            if not data["article"] or not data["type_work"] or not data["equipment"] or not data["mfdate"]:
                QMessageBox.warning(self, "Ошибка", "Заполните все обязательные поля профиля!")
                return False
        else:
            if not data["name"] or not data["departament"] or not data["equipment"] or not data["mfdate"]:
                QMessageBox.warning(self, "Ошибка", "Заполните все обязательные поля продукта!")
                return False
        return True

    def accept(self):
        if self.validate():
            from statusdialog import StatusDialog
            status_dialog = StatusDialog(self)
            if status_dialog.exec() == QDialog.Accepted:
                status, status_id = status_dialog.get_selected_status()
                if status_id is not None:
                    self.selected_status_id = status_id
                    self.valid = True
                    super().accept()
                else:
                    self.valid = False
            else:
                self.valid = False
        else:
            self.valid = False

    def get_selected_status_id(self):
        return getattr(self, 'selected_status_id', None)
