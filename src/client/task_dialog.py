"""
Task creation dialog for ADITIM Monitor Client
"""

from typing import List, Dict, Any, Optional
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QLabel, QLineEdit, QPushButton, QComboBox, QCheckBox,
    QDateEdit, QListWidget, QListWidgetItem, QMessageBox,
    QFormLayout, QGroupBox, QRadioButton, QButtonGroup,
    QTextEdit, QSpinBox
)
from PySide6.QtCore import Qt, QDate, Signal
from PySide6.QtGui import QFont

from .constants import PROFILE_EQUIPMENT, WORK_TYPES, COLORS


class TaskCreateDialog(QDialog):
    """Dialog for creating new tasks"""
    
    task_created = Signal(dict)
    
    def __init__(self, api_client, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.departments = []
        self.profiles = []
        self.products = []
        self.type_works = []
        
        self.setup_ui()
        self.load_data()
        
    def setup_ui(self):
        """Setup user interface"""
        self.setWindowTitle("Добавить задачу")
        self.setMinimumSize(600, 500)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        
        # Tab widget for task types
        self.tab_widget = QTabWidget()
        
        # Profile task tab
        self.profile_tab = QWidget()
        self.setup_profile_tab()
        self.tab_widget.addTab(self.profile_tab, "Инструмент на экструзию")
        
        # Product task tab  
        self.product_tab = QWidget()
        self.setup_product_tab()
        self.tab_widget.addTab(self.product_tab, "Другое")
        
        layout.addWidget(self.tab_widget)
        
        # Bottom buttons
        button_layout = QHBoxLayout()
        
        self.cancel_btn = QPushButton("Отмена")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        self.create_btn = QPushButton("Создать задачу")
        self.create_btn.clicked.connect(self.create_task)
        button_layout.addWidget(self.create_btn)
        
        layout.addLayout(button_layout)
        
        # Apply styles
        self.apply_styles()
        
    def setup_profile_tab(self):
        """Setup profile task creation tab"""
        layout = QVBoxLayout(self.profile_tab)
        
        # Profile selection
        profile_group = QGroupBox("Профиль")
        profile_layout = QFormLayout(profile_group)
        
        self.profile_combo = QComboBox()
        self.profile_combo.setEditable(True)
        profile_layout.addRow("Артикул профиля:", self.profile_combo)
        
        # Work type selection
        work_type_group = QGroupBox("Тип работы")
        work_type_layout = QVBoxLayout(work_type_group)
        
        self.profile_work_type_group = QButtonGroup()
        for i, work_type in enumerate(WORK_TYPES):
            radio = QRadioButton(work_type)
            if i == 0:  # Select first by default
                radio.setChecked(True)
            self.profile_work_type_group.addButton(radio, i)
            work_type_layout.addWidget(radio)
        
        # Equipment selection
        equipment_group = QGroupBox("Оборудование")
        equipment_layout = QVBoxLayout(equipment_group)
        
        self.profile_equipment_checkboxes = []
        for equipment in PROFILE_EQUIPMENT:
            checkbox = QCheckBox(equipment)
            self.profile_equipment_checkboxes.append(checkbox)
            equipment_layout.addWidget(checkbox)
        
        # Common fields
        common_group = QGroupBox("Общие параметры")
        common_layout = QFormLayout(common_group)
        
        self.profile_department_combo = QComboBox()
        common_layout.addRow("Отдел:", self.profile_department_combo)
        
        self.profile_deadline_edit = QDateEdit()
        self.profile_deadline_edit.setDate(QDate.currentDate().addDays(7))
        self.profile_deadline_edit.setCalendarPopup(True)
        common_layout.addRow("Крайний срок:", self.profile_deadline_edit)
        
        # Add all groups to layout
        layout.addWidget(profile_group)
        layout.addWidget(work_type_group)
        layout.addWidget(equipment_group)
        layout.addWidget(common_group)
        layout.addStretch()
        
    def setup_product_tab(self):
        """Setup product task creation tab"""
        layout = QVBoxLayout(self.product_tab)
        
        # Product selection
        product_group = QGroupBox("Продукт")
        product_layout = QFormLayout(product_group)
        
        self.product_combo = QComboBox()
        self.product_combo.setEditable(True)
        product_layout.addRow("Название продукта:", self.product_combo)
        
        # Equipment list
        equipment_group = QGroupBox("Оборудование")
        equipment_layout = QVBoxLayout(equipment_group)
        
        # Equipment input
        equipment_input_layout = QHBoxLayout()
        self.equipment_input = QLineEdit()
        self.equipment_input.setPlaceholderText("Введите название оборудования")
        self.add_equipment_btn = QPushButton("Добавить")
        self.add_equipment_btn.clicked.connect(self.add_equipment)
        
        equipment_input_layout.addWidget(self.equipment_input)
        equipment_input_layout.addWidget(self.add_equipment_btn)
        
        # Equipment list
        self.equipment_list = QListWidget()
        self.remove_equipment_btn = QPushButton("Удалить выбранное")
        self.remove_equipment_btn.clicked.connect(self.remove_equipment)
        
        equipment_layout.addLayout(equipment_input_layout)
        equipment_layout.addWidget(self.equipment_list)
        equipment_layout.addWidget(self.remove_equipment_btn)
        
        # Work type for products
        work_type_group = QGroupBox("Тип работы")
        work_type_layout = QVBoxLayout(work_type_group)
        
        self.product_work_type_combo = QComboBox()
        work_type_layout.addWidget(self.product_work_type_combo)
        
        # Common fields
        common_group = QGroupBox("Общие параметры")
        common_layout = QFormLayout(common_group)
        
        self.product_department_combo = QComboBox()
        common_layout.addRow("Отдел:", self.product_department_combo)
        
        self.product_deadline_edit = QDateEdit()
        self.product_deadline_edit.setDate(QDate.currentDate().addDays(7))
        self.product_deadline_edit.setCalendarPopup(True)
        common_layout.addRow("Крайний срок:", self.product_deadline_edit)
        
        # Add all groups to layout
        layout.addWidget(product_group)
        layout.addWidget(equipment_group)
        layout.addWidget(work_type_group)
        layout.addWidget(common_group)
        layout.addStretch()
        
    def apply_styles(self):
        """Apply custom styles to dialog"""
        style = f"""
            QDialog {{
                background-color: {COLORS["BACKGROUND"]};
                color: {COLORS["TEXT_PRIMARY"]};
            }}
            
            QTabWidget::pane {{
                border: 1px solid {COLORS["PRIMARY"]};
                background-color: {COLORS["SURFACE"]};
            }}
            
            QTabBar::tab {{
                background-color: {COLORS["SURFACE"]};
                color: {COLORS["TEXT_PRIMARY"]};
                padding: 8px 16px;
                margin-right: 2px;
            }}
            
            QTabBar::tab:selected {{
                background-color: {COLORS["PRIMARY"]};
                color: {COLORS["TEXT_PRIMARY"]};
            }}
            
            QGroupBox {{
                font-weight: bold;
                border: 2px solid {COLORS["PRIMARY"]};
                border-radius: 8px;
                margin-top: 1ex;
                padding-top: 10px;
                color: {COLORS["TEXT_PRIMARY"]};
            }}
            
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: {COLORS["PRIMARY"]};
            }}
            
            QPushButton {{
                background-color: {COLORS["PRIMARY"]};
                color: {COLORS["TEXT_PRIMARY"]};
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }}
            
            QPushButton:hover {{
                background-color: {COLORS["SECONDARY"]};
                color: {COLORS["BACKGROUND"]};
            }}
            
            QComboBox, QLineEdit, QDateEdit {{
                background-color: {COLORS["SURFACE"]};
                color: {COLORS["TEXT_PRIMARY"]};
                border: 1px solid {COLORS["PRIMARY"]};
                border-radius: 4px;
                padding: 4px 8px;
            }}
            
            QListWidget {{
                background-color: {COLORS["SURFACE"]};
                color: {COLORS["TEXT_PRIMARY"]};
                border: 1px solid {COLORS["PRIMARY"]};
                border-radius: 4px;
            }}
            
            QCheckBox, QRadioButton {{
                color: {COLORS["TEXT_PRIMARY"]};
                spacing: 8px;
            }}
            
            QCheckBox::indicator, QRadioButton::indicator {{
                width: 16px;
                height: 16px;
            }}
            
            QCheckBox::indicator:checked {{
                background-color: {COLORS["PRIMARY"]};
                border: 1px solid {COLORS["PRIMARY"]};
            }}
            
            QRadioButton::indicator:checked {{
                background-color: {COLORS["PRIMARY"]};
                border: 1px solid {COLORS["PRIMARY"]};
            }}
            
            QLabel {{
                color: {COLORS["TEXT_PRIMARY"]};
            }}
        """
        self.setStyleSheet(style)
        
    def load_data(self):
        """Load data from server"""
        try:
            # Load departments
            self.departments = self.api_client.get_departments()
            for dept in self.departments:
                self.profile_department_combo.addItem(dept["name"], dept["id"])
                self.product_department_combo.addItem(dept["name"], dept["id"])
            
            # Load work types
            self.type_works = self.api_client.get_type_works()
            for work_type in self.type_works:
                self.product_work_type_combo.addItem(work_type["name"], work_type["id"])
            
            # Load profiles
            self.profiles = self.api_client.get_profiles()
            for profile in self.profiles:
                self.profile_combo.addItem(profile["article"], profile["id"])
            
            # Load products
            self.products = self.api_client.get_products()
            for product in self.products:
                self.product_combo.addItem(product["name"], product["id"])
                
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить данные: {e}")
    
    def add_equipment(self):
        """Add equipment to list"""
        equipment_name = self.equipment_input.text().strip()
        if equipment_name:
            self.equipment_list.addItem(equipment_name)
            self.equipment_input.clear()
        
    def remove_equipment(self):
        """Remove selected equipment from list"""
        current_row = self.equipment_list.currentRow()
        if current_row >= 0:
            self.equipment_list.takeItem(current_row)
    
    def create_task(self):
        """Create new task"""
        try:
            current_tab = self.tab_widget.currentIndex()
            
            if current_tab == 0:  # Profile task
                task_data = self.create_profile_task()
            else:  # Product task
                task_data = self.create_product_task()
            
            # Create task via API
            result = self.api_client.create_task(task_data)
            
            QMessageBox.information(self, "Успех", "Задача создана успешно!")
            self.task_created.emit(task_data)
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось создать задачу: {e}")
    
    def create_profile_task(self) -> Dict[str, Any]:
        """Create profile task data"""
        # Get selected equipment
        selected_equipment = []
        for checkbox in self.profile_equipment_checkboxes:
            if checkbox.isChecked():
                selected_equipment.append(checkbox.text())
        
        if not selected_equipment:
            raise ValueError("Выберите хотя бы одно оборудование")
        
        # Get selected work type
        work_type_id = None
        for i, button in enumerate(self.profile_work_type_group.buttons()):
            if button.isChecked():
                work_type_id = self.type_works[i]["id"] if i < len(self.type_works) else 1
                break
        
        # Get or create profile
        profile_text = self.profile_combo.currentText()
        profile_id = self.profile_combo.currentData()
        
        if not profile_id and profile_text:
            # Create new profile
            profile_data = {"article": profile_text}
            profile_result = self.api_client.create_profile(profile_data)
            profile_id = profile_result["id"]
        
        return {
            "id_profile": profile_id,
            "id_departament": self.profile_department_combo.currentData(),
            "equipment": ", ".join(selected_equipment),
            "deadline": self.profile_deadline_edit.date().toString("yyyy-MM-dd"),
            "position": 999,  # Will be auto-assigned by server
            "id_type_work": work_type_id or 1,
            "id_status": 1  # New
        }
    
    def create_product_task(self) -> Dict[str, Any]:
        """Create product task data"""
        # Get equipment list
        equipment_items = []
        for i in range(self.equipment_list.count()):
            equipment_items.append(self.equipment_list.item(i).text())
        
        if not equipment_items:
            raise ValueError("Добавьте хотя бы одно оборудование")
        
        # Get or create product
        product_text = self.product_combo.currentText()
        product_id = self.product_combo.currentData()
        
        if not product_id and product_text:
            # Create new product
            product_data = {
                "name": product_text,
                "id_departament": self.product_department_combo.currentData()
            }
            product_result = self.api_client.create_product(product_data)
            product_id = product_result["id"]
        
        return {
            "id_product": product_id,
            "id_departament": self.product_department_combo.currentData(),
            "equipment": ", ".join(equipment_items),
            "deadline": self.product_deadline_edit.date().toString("yyyy-MM-dd"),
            "position": 999,  # Will be auto-assigned by server
            "id_type_work": self.product_work_type_combo.currentData(),
            "id_status": 1  # New
        }
