"""
Диалог для редактирования существующего изделия.
"""

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


class DialogEditProduct(QDialog):
    """Диалог для редактирования изделия с компонентами"""
    product_updated = Signal(dict)  # Сигнал об успешном обновлении изделия

    def __init__(self, product_data: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.api_product = ApiProduct()
        self.product_data = product_data
        self.product_id = product_data.get('id')
        self.existing_components = []  # Список существующих компонентов

        self.load_ui()
        self.setup_ui()
        self.load_departments()
        self.setup_component_table()
        
        # Заполняем форму данными изделия
        self.fill_form_with_product_data()

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
        self.ui.buttonBox.accepted.connect(self.on_update_clicked)
        self.ui.buttonBox.rejected.connect(self.reject)
        
        # Настройка таблицы компонентов
        self.ui.tableWidget_components.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ui.tableWidget_components.setSelectionMode(QAbstractItemView.SingleSelection)
        
        # Настройка ширины колонок: первая растягивается, вторая фиксированная
        self.ui.tableWidget_components.setColumnWidth(1, 120)  # Количество - фиксированная ширина
        self.ui.tableWidget_components.horizontalHeader().setStretchLastSection(False)
        self.ui.tableWidget_components.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)  # Название - растягивается

    def fill_form_with_product_data(self):
        """Заполняет форму данными редактируемого изделия."""
        # Заполняем основные поля
        name = self.product_data.get('name', '')
        description = self.product_data.get('description', '')
        department_id = self.product_data.get('department_id')
        
        self.ui.lineEdit_name.setText(name)
        self.ui.textEdit_description.setPlainText(description)
        
        # Устанавливаем департамент
        if department_id:
            for i in range(self.ui.comboBox_department.count()):
                if self.ui.comboBox_department.itemData(i) == department_id:
                    self.ui.comboBox_department.setCurrentIndex(i)
                    break

        # Загружаем существующие компоненты
        self.load_existing_components()

    def load_existing_components(self):
        """Загружает существующие компоненты изделия."""
        try:
            self.existing_components = self.api_product.get_product_component(self.product_id)
            self.populate_component_table()
        except Exception as e:
            print(f"Ошибка загрузки компонентов: {e}")
            self.existing_components = []
            self.setup_component_table()

    def populate_component_table(self):
        """Заполняет таблицу компонентов существующими данными."""
        if not self.existing_components:
            self.setup_component_table()
            return

        # Устанавливаем количество строк + 1 пустая строка для добавления новых
        self.ui.tableWidget_components.setRowCount(len(self.existing_components) + 1)
        
        # Заполняем существующие компоненты
        for row, component in enumerate(self.existing_components):
            name = component.get('component_name', '')
            quantity = component.get('quantity', 1)
            self.add_component_row_data(row, name, quantity)
        
        # Добавляем пустую строку для новых компонентов
        self.add_component_row_data(len(self.existing_components), "", 1)

    # =============================================================================
    # Управление департаментами
    # =============================================================================
    def load_departments(self):
        """Загружает департаменты в combobox"""
        departments = api_manager.get_department()
        
        self.ui.comboBox_department.clear()
        self.ui.comboBox_department.addItem("-- Выберите департамент --", 0)
        
        for dept_id, dept_name in departments.items():
            if dept_id > 0:  # Пропускаем пустое значение
                self.ui.comboBox_department.addItem(dept_name, dept_id)

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
        spinbox.setMaximum(9999)
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
    # Валидация и сбор данных
    # =============================================================================
    def validate_data(self) -> bool:
        """Валидация введенных данных"""
        # Проверяем название
        name = self.ui.lineEdit_name.text().strip()
        if not name:
            QMessageBox.warning(self, "Ошибка", "Введите название изделия")
            self.ui.lineEdit_name.setFocus()
            return False
        
        # Проверяем департамент
        dept_id = self.ui.comboBox_department.currentData()
        if not dept_id or dept_id == 0:
            QMessageBox.warning(self, "Ошибка", "Выберите департамент")
            self.ui.comboBox_department.setFocus()
            return False
        
        # Проверяем компоненты
        components = self.get_component_from_table()
        if not components:
            QMessageBox.warning(self, "Ошибка", "Добавьте хотя бы один компонент с названием")
            return False
        
        return True

    def get_component_from_table(self) -> List[Dict[str, Any]]:
        """Извлекает компоненты из таблицы"""
        components = []
        for row in range(self.ui.tableWidget_components.rowCount()):
            # Получаем название компонента
            name_item = self.ui.tableWidget_components.item(row, 0)
            component_name = name_item.text().strip() if name_item else ""
            
            # Пропускаем пустые строки
            if not component_name:
                continue
            
            # Получаем количество из SpinBox
            spinbox = self.ui.tableWidget_components.cellWidget(row, 1)
            quantity = spinbox.value() if spinbox else 1
            
            components.append({
                'component_name': component_name,
                'quantity': quantity,
                'description': None  # Пока без описания, можно добавить позже
            })
        
        return components

    def collect_data(self) -> Dict[str, Any]:
        """Собирает данные из формы"""
        # Основная информация об изделии
        product_data = {
            'name': self.ui.lineEdit_name.text().strip(),
            'department_id': self.ui.comboBox_department.currentData(),
            'description': self.ui.textEdit_description.toPlainText().strip()
        }
        
        # Собираем компоненты
        list_component = self.get_component_from_table()
        
        return {
            'product': product_data,
            'components': list_component
        }

    # =============================================================================
    # Обновление изделия
    # =============================================================================
    @Slot()
    def on_update_clicked(self):
        """Обработчик кнопки обновления изделия"""
        # Валидация
        if not self.validate_data():
            return

        try:
            # Собираем данные
            data = self.collect_data()
            
            # Обновляем изделие
            updated_product = self.api_product.update_product(self.product_id, data['product'])
            
            # Обновляем компоненты
            self.update_product_components(data['components'])

            # Уведомляем об успешном обновлении
            self.product_updated.emit(updated_product)
            
            QMessageBox.information(
                self,
                "Успех",
                "Изделие успешно обновлено!"
            )
            self.accept()

        except Exception as e:
            QMessageBox.critical(
                self,
                "Ошибка",
                f"Произошла ошибка при обновлении изделия:\n{e}"
            )

    def update_product_components(self, new_components: List[Dict[str, Any]]):
        """Обновляет компоненты изделия"""
        try:
            # Удаляем все существующие компоненты
            for existing_comp in self.existing_components:
                try:
                    self.api_product.delete_product_component_by_id(existing_comp['id'])
                except Exception as e:
                    print(f"Ошибка удаления компонента {existing_comp['id']}: {e}")

            # Создаем новые компоненты
            for component_data in new_components:
                try:
                    self.api_product.create_product_component(self.product_id, component_data)
                except Exception as comp_error:
                    print(f"Ошибка создания компонента: {comp_error}")

        except Exception as e:
            print(f"Ошибка обновления компонентов: {e}")
            # Не прерываем процесс, компоненты - дополнительная функциональность
