"""
Содержимое профилей для ADITIM Monitor Client
"""

from PySide6.QtWidgets import QWidget, QMessageBox, QTableWidgetItem
from PySide6.QtCore import QFile
from PySide6.QtUiTools import QUiLoader

from ..resources import UI_PATHS


class ProfilesContent(QWidget):
    """Виджет содержимого профилей"""
    
    def __init__(self):
        super().__init__()
        self.load_ui()
        self.setup_ui()

    def load_ui(self):
        """Загрузка UI из файла"""
        ui_file = QFile(UI_PATHS["PROFILES_CONTENT"])
        ui_file.open(QFile.ReadOnly)
        
        loader = QUiLoader()
        self.ui = loader.load(ui_file)
        ui_file.close()

    def setup_ui(self):
        """Настройка UI компонентов после загрузки"""
        self.ui.pushButton_profile_add.clicked.connect(self.on_add_clicked)
        self.ui.pushButton_profile_edit.clicked.connect(self.on_edit_clicked)
        self.ui.pushButton_profile_delete.clicked.connect(self.on_delete_clicked)
        self.ui.pushButton_sketch_open.clicked.connect(self.on_sketch_open_clicked)
        self.ui.pushButton_autocad_open.clicked.connect(self.on_autocad_open_clicked)
        self.ui.tableWidget_profiles.itemSelectionChanged.connect(self.on_selection_changed)
        self.ui.lineEdit_search.textChanged.connect(self.on_search_changed)

    def on_add_clicked(self):
        """Добавление нового профиля"""
        QMessageBox.information(self, "Добавить", "Добавление нового профиля")

    def on_edit_clicked(self):
        """Редактирование профиля"""
        QMessageBox.information(self, "Редактировать", "Редактирование профиля")

    def on_delete_clicked(self):
        """Удаление профиля"""
        QMessageBox.information(self, "Удалить", "Удаление профиля")

    def on_sketch_open_clicked(self):
        """Открытие эскиза"""
        QMessageBox.information(self, "Эскиз", "Открытие эскиза")

    def on_autocad_open_clicked(self):
        """Открытие чертежа в AutoCAD"""
        QMessageBox.information(self, "AutoCAD", "Открытие в AutoCAD")

    def on_selection_changed(self):
        """Изменение выбранного профиля"""
        selected_items = self.ui.tableWidget_profiles.selectedItems()
        if selected_items:
            self.ui.pushButton_sketch_open.setEnabled(True)
            self.ui.pushButton_autocad_open.setEnabled(True)
            # Обновляем информацию в панели предварительного просмотра
            row = selected_items[0].row()
            article = self.ui.tableWidget_profiles.item(row, 0).text()
            name = self.ui.tableWidget_profiles.item(row, 1).text()
            self.ui.label_profile_article.setText(f"Артикул: {article}")
            self.ui.label_profile_name.setText(f"Название: {name}")
        else:
            self.ui.pushButton_sketch_open.setEnabled(False)
            self.ui.pushButton_autocad_open.setEnabled(False)
            self.ui.label_profile_article.setText("Артикул: -")
            self.ui.label_profile_name.setText("Название: -")

    def on_search_changed(self, text):
        """Поиск по артикулу"""
        # Простая фильтрация по артикулу
        for row in range(self.ui.tableWidget_profiles.rowCount()):
            item = self.ui.tableWidget_profiles.item(row, 0)
            if item:
                visible = text.lower() in item.text().lower()
                self.ui.tableWidget_profiles.setRowHidden(row, not visible)
