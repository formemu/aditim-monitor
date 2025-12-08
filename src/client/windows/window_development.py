from PySide6.QtCore import QFile, Qt, QDate
import base64
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QPixmap, QAction
from PySide6.QtWidgets import  QMenu, QAbstractItemView
from ..constant import UI_PATHS_ABS, get_style_path, ICON_PATHS_ABS
from ..style_util import load_styles
from ..api_manager import api_manager
from PySide6.QtWidgets import QTableWidgetItem

class WindowDevelopment:
    """Окно для управления разработками"""
    def __init__(self):
        super().__init__()
        self.task = None
        self.component_id = None
        self.load_ui()
        self.table = self.ui.tableWidget_taskdev
        self.setup_ui()
        api_manager.data_updated.connect(self.refresh_data)
    
    # =============================================================================
    # ИНИЦИАЛИЗАЦИЯ И ЗАГРУЗКА ИНТЕРФЕЙСА
    # =============================================================================
    def load_ui(self):
        """Загрузка UI из файла"""
        ui_file = QFile(UI_PATHS_ABS["DEVELOPMENT_CONTENT"])
        ui_file.open(QFile.ReadOnly)
        loader = QUiLoader()
        self.ui = loader.load(ui_file)
        ui_file.close()

    def setup_ui(self):
        """Настройка UI компонентов после загрузки"""
        self.ui.setStyleSheet(load_styles(get_style_path("MAIN")))
        self.load_logo()
        self.table.itemClicked.connect(self.on_main_table_clicked)
        # Настройка контекстного меню для таблицы задач
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setFocusPolicy(Qt.NoFocus)
        self.refresh_data()

    def load_logo(self):
        """Загрузка логотипа ADITIM"""
        logo_path = ICON_PATHS_ABS.get("ADITIM_LOGO_MAIN")
        pixmap = QPixmap(logo_path)
        scaled = pixmap.scaled(300, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.ui.label_logo.setPixmap(scaled)
        self.ui.label_logo.setText("")

    def load_and_show_sketch(self, sketch_data):
        """Отображение эскиза профиля"""
        if sketch_data:
            base64_str = sketch_data.split(",", 1)[1] if "," in sketch_data else sketch_data
            image_data = base64.b64decode(base64_str)
            pixmap = QPixmap()
            if pixmap.loadFromData(image_data) and not pixmap.isNull():
                scaled = pixmap.scaled(200, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.ui.label_sketch.setPixmap(scaled)
                self.ui.label_sketch.setText("")
            else:
                self.ui.label_sketch.setText("Ошибка изображения")

        else: self.ui.label_sketch.setText("Эскиз отсутствует")
    
    # =============================================================================
    # УПРАВЛЕНИЕ ДАННЫМИ: ЗАГРУЗКА И ОБНОВЛЕНИЕ
    # =============================================================================
    def refresh_data(self):
        """Обновление данных в окне разработок"""
        self.task = None
        self.component_id = None
        self.clear_info_panel()
        self.update_table_task_dev()

    def update_table_task_dev(self):
        """Обновление таблицы задач разработки"""
        self.table.setRowCount(len(api_manager.table['taskdev']))
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Название", "Срок"])
        for row, task in enumerate(api_manager.table['taskdev']):
            item_name = QTableWidgetItem(self.get_task_name(task))
            item_deadline = QTableWidgetItem(task['deadline'])

            item_name.setData(Qt.UserRole, task['id'])
            item_deadline.setData(Qt.UserRole, task['id'])

            self.table.setItem(row, 0, item_name)
            self.table.setItem(row, 1, item_deadline)
            self.table.setContextMenuPolicy(Qt.CustomContextMenu)
            self.table.customContextMenuRequested.connect(self.show_context_menu_main_table)

    def update_task_info_panel(self):
        """Обновление панели информации о задаче"""
        if self.task:
            self.ui.label_name.setText(self.get_task_name(self.task))
            self.ui.label_description.setText(self.task['description'])
            if self.task['profiletool']:
                sketch_data = self.task['profiletool']['profile']["sketch"]
                self.load_and_show_sketch(sketch_data)
            else: self.ui.label_sketch.setText("Эскиз отсутствует")
            self.update_table_task_component()
            self.ui.tableWidget_component.setContextMenuPolicy(Qt.CustomContextMenu)
            self.ui.tableWidget_component.customContextMenuRequested.connect(self.show_context_menu_component_table)

    def update_table_task_component(self):
        """Обновление таблицы компонентов задачи"""
        self.ui.tableWidget_component.setRowCount(0)
        self.ui.tableWidget_component.setColumnCount(2)
        self.ui.tableWidget_component.setHorizontalHeaderLabels(["Название", "Статус"])
        self.ui.tableWidget_component.setRowCount(len(self.task['profiletool']['component']))
        
        for row, component in enumerate(self.task['profiletool']['component']):
            # Название компонента
            name_item = QTableWidgetItem(component["type"]["name"])
            name_item.setData(Qt.UserRole, component["id"])
            # Последний статус из истории
            last_history = component['history'][-1]
            status_name = last_history["status"]["name"]
            status_item = QTableWidgetItem(status_name)
            status_item.setData(Qt.UserRole, component["id"])
            self.ui.tableWidget_component.setItem(row, 0, name_item)
            self.ui.tableWidget_component.setItem(row, 1, status_item)  
        
        self.ui.tableWidget_component.itemClicked.connect(self.on_component_clicked)

    def get_task_name(self, task):
        """Возвращает название задачи: артикул профиля или имя изделия"""
        if task['profiletool_id']:
            profiletool = api_manager.get_by_id('profiletool', task['profiletool_id'])
            return f"Инструмент {profiletool['profile']['article']}"
        elif task['product_id']:
            product = api_manager.get_by_id('product', task['product_id'])
            return f"Изделие {product['name']}" if product else "Изделие N/A"

    def clear_info_panel(self):
        """Очистка панели информации о задаче"""
        self.ui.label_name.clear()
        self.ui.label_description.clear()
        self.ui.label_sketch.clear()
        self.ui.tableWidget_component.setRowCount(0)

    # =============================================================================
    # ОБРАБОТЧИКИ СОБЫТИЙ
    # =============================================================================
    def on_main_table_clicked(self, item):
        """Обработка клика по элементу таблицы"""
        self.task = api_manager.get_by_id('task', item.data(Qt.UserRole))
        self.update_task_info_panel()

    def on_component_clicked(self, item):
        """Обработка клика по элементу таблицы компонентов"""
        self.component_id = item.data(Qt.UserRole)

    def show_context_menu_main_table(self, pos):
        """Показать контекстное меню для изменения статуса задачи"""
        table = self.ui.tableWidget_taskdev
        menu = QMenu(table)
        status_menu = QMenu("Изменить статус", menu)
        for status in api_manager.directory['task_status']:
            if status['name'] == "Выполнена":
                action = QAction(status['name'], status_menu)
                action.setCheckable(True)
                action.triggered.connect(lambda _, status_id=status['id']: self.change_task_status(status_id))
                status_menu.addAction(action)
        menu.addMenu(status_menu)
        menu.exec(table.viewport().mapToGlobal(pos))

    def show_context_menu_component_table(self, pos):
        """Показать контекстное меню для изменения статуса компонента"""
        table = self.ui.tableWidget_component
        menu = QMenu(table)
        status_menu = QMenu("Изменить статус", menu)
        for status in api_manager.directory['component_status']:
            if status['name'] == 'Разработан':
                action = QAction(status['name'], status_menu)
                action.setCheckable(True)
                action.triggered.connect(lambda _, status_id=status['id']: self.change_component_history(status_id))
                status_menu.addAction(action)
        menu.addMenu(status_menu)
        menu.exec(table.viewport().mapToGlobal(pos))
    
    def change_component_history(self, status):
        """Обновление истории компонентов задачи"""
        
        api_manager.api_profiletool.create_profiletool_component_history(
            self.component_id,
            {
                "date": QDate.currentDate().toString("yyyy-MM-dd"),
                "status_id": status,
                "description": ""
            }
        )

        self.update_table_task_component()

    
    def change_task_status(self, status_id):
        # 1. Обновить статус
        task = api_manager.api_task.update_task_status(self.task['id'], status_id, QDate.currentDate().toString("yyyy-MM-dd"))
        # 2. Получить ВСЕ задачи в статусе "В работе"
        queue = api_manager.table['queue']
        # 3. Формируем новый список ВСЕХ task_ids в правильном порядке
        task_ids = [t['id'] for t in queue]
        # 4. Добавляем или удаляем текущую задачу
        if task['status']['name'] == 'В работе':
            if task['id'] not in task_ids:
                task_ids.append(task['id'])
        else:
            if task['id'] in task_ids:
                task_ids.remove(task['id'])
        # 5. Сохраняем ВСЮ очередь
        api_manager.api_task.reorder_task_queue(task_ids)
        if task['type']['name'] == 'Разработка' and task['status']['name'] == 'В работе':
            status = 2 # Передан в разработку
            self.change_component_history(status, task['component'])

        self.update_table_task_dev()
        self.update_table_task_component()
