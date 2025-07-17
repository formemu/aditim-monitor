"""
Simple Main window for ADITIM Monitor Client
"""

from typing import List, Dict, Any
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QPushButton, 
    QComboBox, QLabel, QStatusBar, QHeaderView,
    QAbstractItemView, QMessageBox
)
from PySide6.QtCore import Qt, QTimer, Signal, Slot, QThread, QObject
from PySide6.QtGui import QAction

from .constants import (
    COLORS, FONTS, SIZES, PATHS, TASK_STATUSES, 
    UPDATE_INTERVAL_MS, MAX_ACTIVE_TASKS
)
from .api_client_sync import ApiClient


class DataWorker(QObject):
    """Worker class for async operations"""
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
        finally:
            self.finished.emit()
    
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
        finally:
            self.finished.emit()


class MainWindow(QMainWindow):
    """Main application window for workers"""
    
    def __init__(self):
        """Initialize main window"""
        super().__init__()
        print("Initializing MainWindow...")
        
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
        self.setGeometry(100, 100, 1200, 800)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        layout = QVBoxLayout(central_widget)
        
        # Status bar
        self.statusBar().showMessage("Инициализация...")
        
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
        
        layout.addWidget(self.tasks_table)
        
    def setup_timer(self) -> None:
        """Setup background update timer"""
        self.timer = QTimer()
        self.timer.timeout.connect(self.start_background_loading)
        self.timer.start(UPDATE_INTERVAL_MS)
        
    def load_styles(self) -> None:
        """Load application styles"""
        try:
            with open(PATHS["MAIN_STYLE"], 'r', encoding='utf-8') as f:
                self.setStyleSheet(f.read())
        except FileNotFoundError:
            print(f"Style file not found: {PATHS['MAIN_STYLE']}")
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
            equipment = task.get("equipment", [])
            if isinstance(equipment, list):
                equipment_str = ", ".join(equipment)
            else:
                equipment_str = str(equipment)
            return f"Профиль {article} - {equipment_str}"
        else:
            product = task.get("product", {})
            name = product.get("name", "N/A")
            return f"Продукт: {name}"
    
    def closeEvent(self, event) -> None:
        """Handle window close event"""
        print("Closing MainWindow...")
        
        # Stop timer
        if hasattr(self, 'timer'):
            self.timer.stop()
        
        # Clean up worker thread
        if self.worker_thread and self.worker_thread.isRunning():
            self.worker_thread.quit()
            self.worker_thread.wait(2000)  # Wait up to 2 seconds
        
        event.accept()
