"""Диалог создания заготовки"""
from PySide6.QtWidgets import (QDialog, QMessageBox, QTableWidgetItem, 
                                QAbstractItemView, QPushButton)
from PySide6.QtCore import QFile, QDate, Qt
from PySide6.QtUiTools import QUiLoader
from ..constant import UI_PATHS_ABS
from ..api_manager import api_manager


class DialogCreateBlank(QDialog):
    """Диалог для создания нового заказа с несколькими позициями заготовок"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.list_position = []  # Список позиций заказа
        self.order_number = None  # Номер заказа
        self.load_ui()
        self.setup_ui()
    
    def load_ui(self):
        """Загрузка UI из файла"""
        ui_file = QFile(UI_PATHS_ABS["DIALOG_CREATE_BLANK"])
        ui_file.open(QFile.ReadOnly)
        loader = QUiLoader()
        self.ui = loader.load(ui_file, self)
        ui_file.close()
        
        # Копируем геометрию и заголовок
        self.setWindowTitle(self.ui.windowTitle())
        self.setLayout(self.ui.layout())
    
    def setup_ui(self):
        """Настройка UI компонентов"""
        # Получение следующего номера заказа
        try:
            result = api_manager.api_blank.get_next_order_number()
            self.order_number = result.get('next_order', 1)
            self.ui.label_order_number.setText(f"Заказ № {self.order_number}")
        except Exception:
            self.order_number = 1
            self.ui.label_order_number.setText(f"Заказ № {self.order_number}")
        
        # Заполнение comboBox материалов
        self.ui.comboBox_material.clear()
        self.ui.comboBox_material.addItem("Не указан", None)
        for material in api_manager.directory.get('blank_material', []):
            self.ui.comboBox_material.addItem(material['name'], material['id'])
        
        # Установка текущей даты для даты заказа (автоматически)
        self.ui.dateEdit_order.setDate(QDate.currentDate())
        self.ui.dateEdit_order.setEnabled(False)  # Нельзя изменить
        
        # Настройка таблицы позиций
        table = self.ui.tableWidget_positions
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["Материал", "Тип", "Размер", "Кол-во", "Удалить"])
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.horizontalHeader().setStretchLastSection(False)
        
        # Подключение сигналов
        self.ui.comboBox_material.currentIndexChanged.connect(self.on_material_changed)
        self.ui.comboBox_blank_type.currentIndexChanged.connect(self.on_blank_type_changed)
        self.ui.pushButton_add_position.clicked.connect(self.on_add_position_clicked)
        self.ui.pushButton_save.clicked.connect(self.on_save_clicked)
        self.ui.pushButton_cancel.clicked.connect(self.reject)
        
        # Заполнение типов заготовок для текущего материала
        self.on_material_changed()
    
    def update_positions_table(self):
        """Обновление таблицы позиций"""
        table = self.ui.tableWidget_positions
        table.setRowCount(len(self.list_position))
        
        for row, position in enumerate(self.list_position):
            # Материал
            material_name = position.get('material_name', 'Не указан')
            table.setItem(row, 0, QTableWidgetItem(material_name))
            
            # Тип заготовки
            type_name = position.get('type_name', 'Не указан')
            table.setItem(row, 1, QTableWidgetItem(type_name))
            
            # Размер
            size = f"{position.get('blank_width', '—')}×{position.get('blank_height', '—')}×{position.get('blank_length', '—')}"
            table.setItem(row, 2, QTableWidgetItem(size))
            
            # Количество
            table.setItem(row, 3, QTableWidgetItem(str(position.get('quantity', 1))))
            
            # Кнопка удаления
            btn_delete = QPushButton("Удалить")
            btn_delete.clicked.connect(lambda checked, r=row: self.on_delete_position_clicked(r))
            table.setCellWidget(row, 4, btn_delete)
    
    def on_material_changed(self):
        """Обработка изменения материала для фильтрации типов заготовок"""
        material_id = self.ui.comboBox_material.currentData()
        
        # Очистка и заполнение comboBox типов заготовок
        self.ui.comboBox_blank_type.clear()
        self.ui.comboBox_blank_type.addItem("Не указан", None)
        
        # Фильтрация типов по выбранному материалу
        for blank_type in api_manager.directory.get('blank_type', []):
            # Показываем только типы с соответствующим материалом
            if material_id is None or blank_type.get('material_id') == material_id:
                type_name = f"{blank_type.get('width', '—')}×{blank_type.get('height', '—')}×{blank_type.get('length', '—')}"
                self.ui.comboBox_blank_type.addItem(type_name, blank_type['id'])
    
    def on_blank_type_changed(self, index):
        """Обработка выбора типа заготовки для автозаполнения размеров"""
        blank_type_id = self.ui.comboBox_blank_type.currentData()
        if blank_type_id:
            # Найти тип заготовки и заполнить размеры
            for blank_type in api_manager.directory.get('blank_type', []):
                if blank_type['id'] == blank_type_id:
                    if blank_type.get('width'):
                        self.ui.spinBox_blank_width.setValue(blank_type['width'])
                    if blank_type.get('height'):
                        self.ui.spinBox_blank_height.setValue(blank_type['height'])
                    if blank_type.get('length'):
                        self.ui.spinBox_blank_length.setValue(blank_type['length'])
                    break
    
    def on_add_position_clicked(self):
        """Добавление позиции в заказ"""
        material_id = self.ui.comboBox_material.currentData()
        material_name = self.ui.comboBox_material.currentText()
        type_name = self.ui.comboBox_blank_type.currentText()
        quantity = self.ui.spinBox_quantity.value()
        
        blank_width = self.ui.spinBox_blank_width.value() if self.ui.spinBox_blank_width.value() > 0 else None
        blank_height = self.ui.spinBox_blank_height.value() if self.ui.spinBox_blank_height.value() > 0 else None
        blank_length = self.ui.spinBox_blank_length.value() if self.ui.spinBox_blank_length.value() > 0 else None
        
        # Добавление позиции в список
        position = {
            "material_id": material_id,
            "material_name": material_name,
            "type_name": type_name,
            "blank_width": blank_width,
            "blank_height": blank_height,
            "blank_length": blank_length,
            "quantity": quantity
        }
        self.list_position.append(position)
        self.update_positions_table()
        
        # Сброс значений
        self.ui.spinBox_quantity.setValue(1)
    
    def on_delete_position_clicked(self, row):
        """Удаление позиции из заказа"""
        if 0 <= row < len(self.list_position):
            del self.list_position[row]
            self.update_positions_table()
    
    def on_save_clicked(self):
        """Сохранение заказа"""
        if not self.list_position:
            QMessageBox.warning(self, "Предупреждение", "Добавьте хотя бы одну позицию в заказ")
            return
        
        date_order = self.ui.dateEdit_order.date().toString("yyyy-MM-dd")
        
        try:
            total_created = 0
            # Создание заготовок для каждой позиции
            for position in self.list_position:
                blank_data = {
                    "order": self.order_number,
                    "material_id": position.get("material_id"),
                    "date_order": date_order,
                    "date_arrival": None,
                    "date_product": None,
                    "blank_width": position.get("blank_width"),
                    "blank_height": position.get("blank_height"),
                    "blank_length": position.get("blank_length"),
                    "product_width": None,
                    "product_height": None,
                    "product_length": None,
                    "profiletool_component_id": None,
                    "product_component_id": None,
                }
                
                quantity = position.get("quantity", 1)
                if quantity == 1:
                    api_manager.api_blank.create_blank(blank_data)
                    total_created += 1
                else:
                    api_manager.api_blank.create_list_blank(blank_data, quantity)
                    total_created += quantity
            
            QMessageBox.information(
                self, 
                "Успех", 
                f"Заказ № {self.order_number} создан\nВсего заготовок: {total_created}"
            )
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось создать заказ: {str(e)}")
