from PySide6.QtCore import Qt, QDate
import base64
from PySide6.QtGui import QPixmap, QAction
from PySide6.QtWidgets import QMenu, QAbstractItemView

from ..base_window import BaseWindow
from ..base_table import BaseTable
from ..constant import UI_PATHS_ABS
from ..api_manager import api_manager


class WindowDevelopment(BaseWindow):
    """Окно для управления разработками"""
    def __init__(self):
        self.task = None
        self.component_id = None
        super().__init__(UI_PATHS_ABS["DEVELOPMENT_CONTENT"], api_manager)
    
    # =============================================================================
    # ИНИЦИАЛИЗАЦИЯ И ЗАГРУЗКА ИНТЕРФЕЙСА
    # =============================================================================
    def setup_ui(self):
        """Настройка UI компонентов после загрузки"""
        self.apply_styles()
        self.load_logo()
        self.ui.tableWidget_taskdev.itemClicked.connect(self.on_main_table_clicked)
        # Настройка контекстного меню для таблицы задач
        self.ui.tableWidget_taskdev.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.tableWidget_taskdev.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ui.tableWidget_taskdev.setSelectionMode(QAbstractItemView.SingleSelection)
        self.ui.tableWidget_taskdev.setFocusPolicy(Qt.NoFocus)
        self.refresh_data()

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
        BaseTable.populate_table(
            self.ui.tableWidget_taskdev,
            ["Название", "Срок"],
            api_manager.table['taskdev'],
            func_row_mapper=lambda task: [
                self.get_task_name(task),
                task['deadline']
            ],
            func_id_getter=lambda task: task['id']
        )
        
        self.ui.tableWidget_taskdev.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.tableWidget_taskdev.customContextMenuRequested.connect(self.show_context_menu_main_table)

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
            

    def update_table_task_component(self):
        """Обновление таблицы компонентов задачи"""
        table = self.ui.tableWidget_component
        
        # Маппер для строки компонента
        def map_component_row(component):
            # Последний статус из истории
            history = component.get('history', [])
            if history:
                last_history = history[-1]
                status_name = last_history["status"]["name"]
            else:
                status_name = ""
            
            return [
                component["type"]["name"],
                status_name,
                component.get("description", "") or ""
            ]
        
        BaseTable.populate_table(
            table,
            ["Название", "Статус", "Описание"],
            self.task['profiletool']['component'],
            func_row_mapper=map_component_row,
            func_id_getter=lambda c: c["id"]
        )

        table.itemClicked.connect(self.on_component_clicked)
        table.setContextMenuPolicy(Qt.CustomContextMenu)
        table.customContextMenuRequested.connect(self.show_context_menu_component_table)

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
        task_id = BaseTable.get_selected_id(self.ui.tableWidget_taskdev)
        self.task = api_manager.get_by_id('task', task_id)
        self.update_task_info_panel()

    def on_component_clicked(self, item):
        """Обработка клика по элементу таблицы компонентов"""
        self.component_id = BaseTable.get_selected_id(self.ui.tableWidget_component)

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
