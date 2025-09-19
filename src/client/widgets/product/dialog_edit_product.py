"""Диалог для редактирования существующего изделия."""
from typing import Dict, Any, List
from PySide6.QtWidgets import (QDialog, QMessageBox, QTableWidgetItem, QSpinBox, QAbstractItemView, QHeaderView)
from PySide6.QtCore import Signal, QFile, Qt, Slot
from PySide6.QtUiTools import QUiLoader
from ...constant import UI_PATHS_ABS
from ...api_manager import api_manager
import warnings


class DialogEditProduct(QDialog):
    """Диалог для редактирования изделия с компонентами"""
    
    def __init__(self, product, parent=None):
        super().__init__(parent)
        self.product = product

        self.load_ui()
        self.setup_ui()
        self.load_department()
        # Заполняем форму данными изделия
        self.fill_product()
        self.fill_component()

    def load_ui(self):
        """Загружает UI из файла"""
        ui_file = QFile(UI_PATHS_ABS["DIALOG_EDIT_PRODUCT"])
        ui_file.open(QFile.ReadOnly)
        
        loader = QUiLoader()
        self.ui = loader.load(ui_file, self)
        ui_file.close()

        # Устанавливаем заголовок и свойства диалога
        self.setWindowTitle("Редактирование изделия")
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

    def fill_product(self):
        """Заполняет форму данными редактируемого изделия."""
        # Заполняем основные поля
        name = self.product['name']
        description = self.product['description']
        department_id = self.product['department']['id']
        self.ui.lineEdit_name.setText(name)
        self.ui.textEdit_description.setPlainText(description)
        # Устанавливаем департамент
        if department_id:
            for i in range(self.ui.comboBox_department.count()):
                if self.ui.comboBox_department.itemData(i) == department_id:
                    self.ui.comboBox_department.setCurrentIndex(i)
                    break

        # Загружаем существующие компоненты
    def fill_component(self):
        """Загружает существующие компоненты изделия."""
        self.ui.tableWidget_components.setRowCount(len(self.product['component']) + 1)
        # Заполняем существующие компоненты
        for row, component in enumerate(self.product['component']):
            name = component['name']
            quantity = component['quantity']
            self.add_component_row_data(row, name, quantity)
        # Добавляем пустую строку для новых компонентов
        self.add_component_row_data(len(self.product['component']), "", 1)

    # =============================================================================
    # Управление департаментами
    # =============================================================================
    def load_department(self):
        """Загружает департаменты в combobox"""
        department = api_manager.directory['department']
        for dep in department:
            self.ui.comboBox_department.addItem(dep['name'], dep['id'])

    # =============================================================================
    # Управление таблицей компонентов
    # =============================================================================
    def setup_new_table_component(self):
        """Настраивает таблицу компонентов с одной начальной строкой"""
        self.ui.tableWidget_components.setRowCount(1)
        self.add_component_row_data(0, "", 1)

    def add_component_row_data(self, row, name, quantity):
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
        spinbox.setMaximum(99)
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
    # Cбор данных
    # =============================================================================
    def get_component_from_table(self):
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
                'name':name,
                'quantity': quantity,
                'description': None  # Пока без описания, можно добавить позже
            })
        
        return list_component

    # =============================================================================
    # Обновление изделия
    # =============================================================================
    @Slot()
    def update_product(self):
        """Обработчик кнопки обновления изделия"""
            # Собираем данные
        product = {
            'name': self.ui.lineEdit_name.text().strip(),
            'department_id': self.ui.comboBox_department.currentData(),
            'description': self.ui.textEdit_description.toPlainText().strip()
        }
        # Обновляем изделие
        api_manager.api_product.update_product(self.product['id'], product)

    def update_product_component(self):
        """Обновляет компоненты изделия"""
        if self.product['component']:
            api_manager.api_product.delete_product_component(self.product['id'])
        for component in self.get_component_from_table():
            api_manager.api_product.create_product_component(self.product['id'], component)
    
    def accept(self):
        self.update_product()
        self.update_product_component()
        super().accept()