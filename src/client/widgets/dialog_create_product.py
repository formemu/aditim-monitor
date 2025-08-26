"""Диалог для создания изделия"""

from typing import Dict, Any, Optional, List
from PySide6.QtWidgets import (QDialog, QMessageBox, QTableWidgetItem, 
                               QCheckBox, QSpinBox, QAbstractItemView, QHeaderView)
from PySide6.QtCore import Signal, QFile, Qt, Slot
from PySide6.QtUiTools import QUiLoader

from ..constant import UI_PATHS_ABS
from ..api.api_product import ApiProduct
from ..api_manager import api_manager
from ..style_util import load_styles
import warnings


class DialogCreateProduct(QDialog):
    """Диалог для создания изделия с компонентами"""
    def __init__(self, parent=None):
        super().__init__(parent)

        self.load_ui()
        self.load_department()
        self.setup_ui()
        self.setup_component_table()

    def load_ui(self):
        """Загружает UI из файла"""
        ui_file = QFile(UI_PATHS_ABS["DIALOG_CREATE_PRODUCT"])
        ui_file.open(QFile.ReadOnly)
        loader = QUiLoader()
        self.ui = loader.load(ui_file, self)
        ui_file.close()
        # Устанавливаем заголовок и свойства диалога
        self.setWindowTitle("Создание изделия")
        self.setModal(True)
        self.setLayout(self.ui.layout())

    def setup_ui(self):
        """Настройка UI компонентов"""
        # Подключаем кнопки
        self.ui.buttonBox.accepted.connect(self.accept)
        self.ui.buttonBox.rejected.connect(self.reject)
        # Настройка таблицы компонентов
        self.ui.tableWidget_components.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ui.tableWidget_components.setSelectionMode(QAbstractItemView.SingleSelection)
        # Настройка ширины колонок: первая растягивается, вторая фиксированная
        self.ui.tableWidget_components.setColumnWidth(1, 120)  # Количество - фиксированная ширина
        self.ui.tableWidget_components.horizontalHeader().setStretchLastSection(False)
        self.ui.tableWidget_components.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)  # Название - растягивается

    # =============================================================================
    # Управление департаментами
    # =============================================================================
    def load_department(self):
        """Загружает департаменты в combobox"""
        self.ui.comboBox_department.clear()
        for department in api_manager.department:
            name = department['name']
            department_id = department['id']
            self.ui.comboBox_department.addItem(name, department_id)
            
    # =============================================================================
    # Управление таблицей компонентов
    # =============================================================================
    def setup_component_table(self):
        """Настраивает таблицу компонентов с одной начальной строкой"""
        self.ui.tableWidget_components.setRowCount(1)
        self.add_component_row_data(0, "", 1)

    def add_component_row_data(self, row: int, name: str = "", quantity: int = 1):
        """Добавляет данные в строку компонента"""
        with warnings.catch_warnings(record=True):
            try:
                self.ui.tableWidget_components.itemChanged.disconnect(self.on_component_item_changed)
            except TypeError:
                pass
            except RuntimeError:
                pass
        # Название компонента (редактируемое поле)
        name_item = QTableWidgetItem(name)
        name_item.setFlags(name_item.flags() | Qt.ItemIsEditable)
        self.ui.tableWidget_components.setItem(row, 0, name_item)
        # SpinBox для количества
        spinbox = QSpinBox()
        spinbox.setMinimum(1)
        spinbox.setMaximum(quantity)
        spinbox.setValue(quantity)
        self.ui.tableWidget_components.setCellWidget(row, 1, spinbox)
        
        # Подключаем обработчик изменения текста для автоматического управления строками
        self.ui.tableWidget_components.itemChanged.connect(self.on_component_item_changed)

    @Slot()
    def on_component_item_changed(self, item):
        """Обработчик изменения элемента в таблице компонентов"""
        if item.column() == 0:  # Реагируем только на изменения в колонке "Название"
            row = item.row()
            text = item.text().strip()
            if text:  # Если строка заполнена
                # Проверяем, нужно ли добавить новую пустую строку
                is_last_row = row == self.ui.tableWidget_components.rowCount() - 1
                if is_last_row:
                    # Добавляем новую пустую строку
                    self.ui.tableWidget_components.setRowCount(row + 2)
                    self.add_component_row_data(row + 1, "", 1)
            else:  # Если строка очищена
                # Удаляем строку, если она не единственная
                if self.ui.tableWidget_components.rowCount() > 1:
                    self.ui.tableWidget_components.removeRow(row)

    # =============================================================================
    # Сбор данных
    # =============================================================================
    def get_component(self):
        """Извлекает компоненты из таблицы"""
        list_component = []
        for row in range(self.ui.tableWidget_components.rowCount()):
            # Получаем название компонента
            name_item = self.ui.tableWidget_components.item(row, 0)
            name = name_item.text().strip() if name_item else ""
            # Пропускаем пустые строки
            if not name:
                continue
            # Получаем количество из SpinBox
            spinbox = self.ui.tableWidget_components.cellWidget(row, 1)
            quantity = spinbox.value() if spinbox else 1
            list_component.append({
                'name': name,
                'quantity': quantity,
                'description': None  # Пока без описания, можно добавить позже
            })
        return list_component

    # =============================================================================
    # Создание изделия
    # =============================================================================
    @Slot()
    def create_product(self):
        """Обработчик кнопки создания изделия"""
        product = {
            'name': self.ui.lineEdit_name.text().strip(),
            'department_id': self.ui.comboBox_department.currentData(),
            'description': self.ui.textEdit_description.toPlainText().strip()
        }
        # Создаем изделие
        result = api_manager.api_product.create_product(product)
        product_id = result['id']
        # Создаем выбранные компоненты
        for component in self.get_component():
            api_manager.api_product.create_product_component(product_id, component)

    
    def accept(self):
        self.create_product()
        return super().accept()
    