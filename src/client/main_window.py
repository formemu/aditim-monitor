"""
Main window for ADITIM Monitor Client
"""

from typing import List, Dict, Any
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QPushButton, 
    QComboBox, QLabel,  QHeaderView,
    QAbstractItemView, QMessageBox
)
from PySide6.QtCore import Qt, QTimer, Signal, Slot, QThread, QObject
from PySide6.QtGui import QPixmap, QIcon
import os

from .style_utils import load_styles_with_constants
from .constants import (
    COLORS, SIZES, UPDATE_INTERVAL_MS
)
from .api_client import ApiClient
from .widgets.dialog_create_profile import DialogCreateProfile
from .exceptions import DataLoadError
from .error_handler import handle_api_error


class DataWorker(QObject):
    """Worker class for background operations"""
    finished = Signal()
    tasks_loaded = Signal(list)
    filters_loaded = Signal(dict)
    error_occurred = Signal(str)
    
    def __init__(self, api_client):
        super().__init__()
        self.api_client = api_client
    
    @Slot()
    def load_tasks(self):
        """Load tasks from server"""
        try:
            tasks = self.api_client.get_tasks()
            self.tasks_loaded.emit(tasks)
        except Exception as e:
            self.error_occurred.emit(str(e))
    
    @Slot()
    def load_filters(self):
        """Load filter data from server"""
        try:
            statuses = self.api_client.get_statuses()
            departments = self.api_client.get_departments()
            filters = {"statuses": statuses, "departments": departments}
            self.filters_loaded.emit(filters)
        except Exception as e:
            self.error_occurred.emit(str(e))


class MainWindow(QMainWindow):
    """Main application window for workers"""
    
    def __init__(self):
        """Initialize main window"""
        super().__init__()
        print("Initializing ADITIM Monitor Client...")
        
        self.api_client = ApiClient()
        self.current_tasks: List[Dict[str, Any]] = []
        self.is_loading = False
        
        # Thread management
        self.worker_thread = None
        self.worker = None
        
        self.setup_ui()
        self.setup_timer()
        self.load_styles()
        
        # Load data after a short delay
        QTimer.singleShot(2000, self.start_background_loading)
    
    def setup_ui(self) -> None:
        """Setup user interface"""
        self.setWindowTitle("ADITIM Monitor - Задачи")
        self.setGeometry(100, 100, SIZES["MAIN_WINDOW_WIDTH"], SIZES["MAIN_WINDOW_HEIGHT"])
        
        # Set window icon - use smaller, cleaner version for window icon
        ico_path = os.path.join(os.path.dirname(__file__), "resources", "icons", "aditim_logo.ico")
        icon_32_path = os.path.join(os.path.dirname(__file__), "resources", "icons", "aditim_logo_32x32.png")
        png_logo_path = os.path.join(os.path.dirname(__file__), "resources", "icons", "aditim_logo.png")
        
        if os.path.exists(ico_path):
            self.setWindowIcon(QIcon(ico_path))
        elif os.path.exists(icon_32_path):
            self.setWindowIcon(QIcon(icon_32_path))
        elif os.path.exists(png_logo_path):
            # Create a smaller icon from the original PNG
            pixmap = QPixmap(png_logo_path)
            scaled_icon = pixmap.scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.setWindowIcon(QIcon(scaled_icon))
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        layout = QVBoxLayout(central_widget)
        
        # Status bar
        self.statusBar().showMessage("Инициализация...")
        
        # Header with logo
        header_layout = QHBoxLayout()
        
        # Title
        title_label = QLabel("ЦЕХ МЕТАЛЛООБРАБОТКИ")
        title_label.setObjectName("header_title")
        header_layout.addWidget(title_label)
        
        # Spacer to push logo to the right
        header_layout.addStretch()
        
        # Logo - bigger and on the right
        logo_label = QLabel()
        if os.path.exists(png_logo_path):
            pixmap = QPixmap(png_logo_path)
            # Calculate size as 1/3 of window width, with max height of 120px
            window_width = SIZES["MAIN_WINDOW_WIDTH"]
            logo_width = window_width // 3
            logo_height = min(120, logo_width)  # Keep aspect ratio in mind
            
            # Scale logo to larger size
            scaled_pixmap = pixmap.scaled(
                logo_width, logo_height, 
                Qt.AspectRatioMode.KeepAspectRatio, 
                Qt.TransformationMode.SmoothTransformation
            )
            logo_label.setPixmap(scaled_pixmap)
        logo_label.setObjectName("logo_label")
        logo_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        header_layout.addWidget(logo_label)
        
        layout.addLayout(header_layout)
        
        # Filter section
        filter_layout = QHBoxLayout()
        
        filter_layout.addWidget(QLabel("Статус:"))
        self.status_filter = QComboBox()
        self.status_filter.addItem("Все", "")
        filter_layout.addWidget(self.status_filter)
        
        filter_layout.addWidget(QLabel("Отдел:"))
        self.department_filter = QComboBox()
        self.department_filter.addItem("Все", "")
        filter_layout.addWidget(self.department_filter)
        
        # Refresh button
        self.refresh_btn = QPushButton("Обновить")
        self.refresh_btn.clicked.connect(self.start_background_loading)
        filter_layout.addWidget(self.refresh_btn)
        
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        
        # Tasks table
        self.tasks_table = QTableWidget()
        self.tasks_table.setColumnCount(6)
        self.tasks_table.setHorizontalHeaderLabels([
            "ID", "Тип", "Описание", "Крайний срок", "Статус", "Отдел"
        ])
        
        # Configure table
        header = self.tasks_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tasks_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tasks_table.setAlternatingRowColors(True)
        
        # Enable drag and drop for reordering
        self.tasks_table.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        
        # Enable double-click to edit status
        self.tasks_table.itemDoubleClicked.connect(self.edit_task_status)
        
        layout.addWidget(self.tasks_table)
        
        # Bottom buttons
        button_layout = QHBoxLayout()
        
        self.create_product_btn = QPushButton("Создать профиль")
        self.create_product_btn.clicked.connect(self.create_product)
        self.create_product_btn.setObjectName("primary_button")  # Для стилизации
        button_layout.addWidget(self.create_product_btn)
        
        self.delete_task_btn = QPushButton("Удалить задачу")
        self.delete_task_btn.clicked.connect(self.delete_selected_task)
        button_layout.addWidget(self.delete_task_btn)
        
        button_layout.addStretch()
        
        # Add info label
        info_label = QLabel("💡 Дважды кликните на статус для изменения")
        info_label.setObjectName("info_label")
        button_layout.addWidget(info_label)
        
        layout.addLayout(button_layout)
        
    def setup_timer(self) -> None:
        """Setup background update timer"""
        self.timer = QTimer()
        self.timer.timeout.connect(self.start_background_loading)
        self.timer.start(UPDATE_INTERVAL_MS)
        
    def load_styles(self) -> None:
        """Load application styles"""
        try:
            # Load main styles from template file with constants
            stylesheet = load_styles_with_constants("src/client/resources/styles/main_template.qss")
            self.setStyleSheet(stylesheet)
        except Exception as e:
            print(f"Error loading styles: {e}")
    
    def start_background_loading(self):
        """Start background data loading"""
        if self.is_loading:
            return
            
        print("Starting background loading...")
        self.is_loading = True
        self.statusBar().showMessage("Загрузка данных...")
        
        # Create worker and thread
        self.worker = DataWorker(self.api_client)
        self.worker_thread = QThread()
        
        # Move worker to thread
        self.worker.moveToThread(self.worker_thread)
        
        # Connect signals
        self.worker_thread.started.connect(self.worker.load_tasks)
        self.worker.tasks_loaded.connect(self.on_tasks_loaded)
        self.worker.error_occurred.connect(self.on_error)
        self.worker.finished.connect(self.on_loading_finished)
        self.worker.finished.connect(self.worker_thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)
        
        # Start thread
        self.worker_thread.start()
    
    @Slot(list)
    def on_tasks_loaded(self, tasks):
        """Handle tasks loaded"""
        print(f"Loaded {len(tasks)} tasks")
        self.current_tasks = tasks
        self.update_tasks_table()
        self.statusBar().showMessage(f"Загружено задач: {len(tasks)}")
    
    @Slot(str)
    def on_error(self, error_msg):
        """Handle error"""
        print(f"Error: {error_msg}")
        self.statusBar().showMessage(f"Ошибка: {error_msg}")
        handle_api_error(self, error_msg)
    
    @Slot()
    def on_loading_finished(self):
        """Handle loading finished"""
        self.is_loading = False
        print("Loading finished")
    
    def update_tasks_table(self):
        """Update tasks table with current data"""
        self.tasks_table.setRowCount(len(self.current_tasks))
        
        for row, task in enumerate(self.current_tasks):
            # ID
            self.tasks_table.setItem(row, 0, QTableWidgetItem(str(task.get("id", ""))))
            
            # Type
            task_type = "Профиль" if task.get("id_profile") else "Продукт"
            self.tasks_table.setItem(row, 1, QTableWidgetItem(task_type))
            
            # Description
            description = self.get_task_description(task)
            self.tasks_table.setItem(row, 2, QTableWidgetItem(description))
            
            # Deadline
            deadline = task.get("deadline", "")
            if deadline:
                deadline = deadline.split("T")[0]  # Remove time part
            self.tasks_table.setItem(row, 3, QTableWidgetItem(deadline))
            
            # Status
            status_name = task.get("status", {}).get("name", "N/A")
            self.tasks_table.setItem(row, 4, QTableWidgetItem(status_name))
            
            # Department
            dept_name = task.get("departament", {}).get("name", "N/A")
            self.tasks_table.setItem(row, 5, QTableWidgetItem(dept_name))
    
    def get_task_description(self, task: Dict[str, Any]) -> str:
        """Generate task description"""
        if task.get("id_profile"):
            profile = task.get("profile", {})
            article = profile.get("article", "N/A")
            equipment = task.get("equipment", "")
            return f"Профиль {article} - {equipment}"
        else:
            product = task.get("product", {})
            name = product.get("name", "N/A")
            equipment = task.get("equipment", "")
            return f"Продукт: {name} - {equipment}"
    
    def create_product(self):
        """Open profile creation dialog"""
        dialog = DialogCreateProfile(self.api_client, self)
        dialog.profile_created.connect(self.on_profile_created)
        dialog.exec()
    
    @Slot(dict)
    def on_profile_created(self, profile_data):
        """Handle profile created successfully"""
        # Можно добавить обновление списка профилей или другую логику
        QMessageBox.information(
            self,
            "Профиль создан",
            f"Профиль '{profile_data.get('article', 'N/A')}' успешно создан!"
        )
    
    def edit_task_status(self, item):
        """Edit task status on double-click"""
        if item.column() == 4:  # Status column
            row = item.row()
            if row < len(self.current_tasks):
                task = self.current_tasks[row]
                self.show_status_change_dialog(task)
    
    def show_status_change_dialog(self, task):
        """Show dialog to change task status"""
        try:
            # Get available statuses
            statuses = self.api_client.get_statuses()
            
            # Create simple input dialog
            from PySide6.QtWidgets import QInputDialog
            
            status_names = [status["name"] for status in statuses]
            current_status = task.get("status", {}).get("name", "Новая")
            
            new_status, ok = QInputDialog.getItem(
                self, 
                "Изменить статус",
                f"Выберите новый статус для задачи #{task['id']}:",
                status_names,
                status_names.index(current_status) if current_status in status_names else 0,
                False
            )
            
            if ok and new_status != current_status:
                # Find status ID
                new_status_id = None
                for status in statuses:
                    if status["name"] == new_status:
                        new_status_id = status["id"]
                        break
                
                if new_status_id:
                    # Update task status
                    update_data = {"id_status": new_status_id}
                    self.api_client.update_task(task["id"], update_data)
                    
                    QMessageBox.information(self, "Успех", f"Статус задачи изменён на '{new_status}'")
                    self.start_background_loading()  # Refresh
                    
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось изменить статус: {e}")
    
    def delete_selected_task(self):
        """Delete selected task"""
        current_row = self.tasks_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Предупреждение", "Выберите задачу для удаления")
            return
        
        if current_row >= len(self.current_tasks):
            QMessageBox.warning(self, "Ошибка", "Некорректный выбор задачи")
            return
        
        task = self.current_tasks[current_row]
        task_id = task["id"]
        
        # Get task description for confirmation
        description = self.get_task_description(task)
        
        reply = QMessageBox.question(
            self, 
            "Подтверждение удаления",
            f"Вы уверены, что хотите удалить задачу:\n{description}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.api_client.delete_task(task_id)
                QMessageBox.information(self, "Успех", "Задача удалена")
                self.start_background_loading()  # Refresh tasks
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Не удалось удалить задачу: {e}")
    
    def closeEvent(self, event) -> None:
        """Handle window close event"""
        print("Closing ADITIM Monitor Client...")

        # Stop timer
        if hasattr(self, 'timer'):
            self.timer.stop()

        # Clean up worker thread
        if self.worker_thread is not None:
            try:
                if self.worker_thread.isRunning():
                    self.worker_thread.quit()
                    self.worker_thread.wait()
            except RuntimeError:
                # Thread object already deleted, ignore
                pass
            self.worker_thread = None

        event.accept()
