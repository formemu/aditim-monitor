"""Содержимое задач для ADITIM Monitor Client"""
from PySide6.QtWidgets import QWidget, QTableWidgetItem, QAbstractItemView,  QMenu, QHeaderView, QDialog
from PySide6.QtCore import QFile, Qt, QTimer
from PySide6.QtGui import QAction
from PySide6.QtUiTools import QUiLoader
from ..constant import UI_PATHS_ABS as UI_PATHS, get_style_path
from ..widgets.dialog_create_task import DialogCreateTask
from ..style_util import load_styles
from ..api_manager import api_manager


class WindowTask(QWidget):
    """Виджет содержимого задач"""
    def __init__(self):
        super().__init__()
        self.task = None
        self.selected_row = None
        self.load_ui()
        self.setup_ui()

    # =============================================================================
    # ИНИЦИАЛИЗАЦИЯ И ЗАГРУЗКА ИНТЕРФЕЙСА
    # =============================================================================
    def load_ui(self):
        """Загрузка UI из файла"""
        ui_file = QFile(UI_PATHS["TASK_CONTENT"])
        ui_file.open(QFile.ReadOnly)
        loader = QUiLoader()
        self.ui = loader.load(ui_file)
        ui_file.close()

    def setup_ui(self):
        """Настройка UI компонентов"""
        self.ui.setStyleSheet(load_styles(get_style_path("MAIN")))
        # Настройка контекстного меню для таблицы задач
        self.ui.tableWidget_tasks.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.tableWidget_tasks.customContextMenuRequested.connect(self.show_context_menu)
        # Подключение сигналов
        self.ui.pushButton_task_add.clicked.connect(self.on_create_task)
        self.ui.pushButton_task_delete.clicked.connect(self.on_delete_clicked)
        self.ui.tableWidget_tasks.itemSelectionChanged.connect(self.on_selection_changed)
        self.ui.lineEdit_search.textChanged.connect(self.filter_table)
        # Настройка таблицы задач
        table = self.ui.tableWidget_tasks
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setSelectionMode(QAbstractItemView.SingleSelection)
        table.setFocusPolicy(Qt.NoFocus)
        # Таймер автообновления
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.refresh_data)
    # =============================================================================
    # УПРАВЛЕНИЕ ДАННЫМИ: ЗАГРУЗКА И ОБНОВЛЕНИЕ
    # =============================================================================
    def refresh_data(self):
        """Принудительное обновление данных"""
        api_manager.refresh_task_async()
        self.update_task_table()
        if self.selected_row is not None:
            self.update_task_info_panel()

    # =============================================================================
    # ОТОБРАЖЕНИЕ ДАННЫХ: ТАБЛИЦЫ И ИНФОРМАЦИОННЫЕ ПАНЕЛИ
    # =============================================================================
    def update_task_table(self):
        """Обновление таблицы задач с корректным отображением и заполнением по ширине"""
        table = self.ui.tableWidget_tasks
        table.setRowCount(len(api_manager.task))
        table.setColumnCount(6) 
        # Заголовки столбцов
        table.setHorizontalHeaderLabels(["Название", "Статус", "Позиция", "Срок", "Создано", "Описание"])
        header = table.horizontalHeader()
        for col in range(table.columnCount() - 1):
            header.setSectionResizeMode(col, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(table.columnCount() - 1, QHeaderView.Stretch)

        for row, task in enumerate(api_manager.task):
            name = self.get_task_name(task)
            table.setItem(row, 0, QTableWidgetItem(name))
            status = task['status']['name']
            table.setItem(row, 1, QTableWidgetItem(status))
            position = str(task['position'])
            table.setItem(row, 2, QTableWidgetItem(position))
            deadline = task['deadline_on']
            table.setItem(row, 3, QTableWidgetItem(deadline))
            created = task['created_at']
            table.setItem(row, 4, QTableWidgetItem(created))
            description = task['description']
            table.setItem(row, 5, QTableWidgetItem(description))

    def update_task_info_panel(self):
        """Обновление панели информации о задаче"""
        self.task = api_manager.task[self.selected_row]
        name = self.get_task_name(self.task)
        deadline = self.task['deadline_on']
        created = self.task['created_at']
        status = self.task['status']['name']
        self.ui.label_task_name.setText(f"Название: {name}")
        self.ui.label_task_info.setText(f"Статус: {status} | Срок: {deadline} | Создано: {created}")

    def get_task_name(self, task):
        """Возвращает название задачи: артикул профиля или имя изделия"""
        if task['profile_tool_id']:
            profile_tool = api_manager.get_profile_tool_by_id(task['profile_tool_id'])
            return f"Инструмент {profile_tool['profile']['article']}"
        elif task['product_id']:
            product = api_manager.get_product_by_id(task['product_id'])
            return f"Изделие {product['name']}" if product else "Изделие N/A"
        return print("ошибка тут: WindowTask.get_task_name")

    def clear_task_info_panel(self):
        """Очистка панели задачи"""
        self.ui.label_task_name.setText("Название: -")
        self.ui.label_task_info.setText("Статус: - | Срок: - | Создано: -")

    def load_component(self, task_id):
        """Загрузка компонентов задачи по её идентификатору. """
        list_component = self.api_task.get_task_component(task_id)
        """Обновление таблицы компонентов"""
        table = self.ui.tableWidget_components
        table.setRowCount(len(list_component))

        # Проверяем по первому элементу, какой тип компонента
        if list_component and list_component[0].get('product_component_id'):
            table.setColumnCount(3)
            header = table.horizontalHeader()
            header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(1, QHeaderView.Stretch)
            header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
            table.setHorizontalHeaderLabels(["№", "Название", "Количество"])
            for row, comp in enumerate(list_component):
                num_item = QTableWidgetItem(str(row + 1))
                table.setItem(row, 0, num_item)
                name_item = QTableWidgetItem(comp.get('name', ''))
                table.setItem(row, 1, name_item)
                qty_item = QTableWidgetItem(str(comp.get('quantity', '')))
                table.setItem(row, 2, qty_item)
        else:
            table.setColumnCount(2)
            header = table.horizontalHeader()
            header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(1, QHeaderView.Stretch)
            table.setHorizontalHeaderLabels(["№", "Название"])
            for row, comp in enumerate(list_component):
                num_item = QTableWidgetItem(str(row + 1))
                table.setItem(row, 0, num_item)
                name_item = QTableWidgetItem(comp.get('name', ''))
                table.setItem(row, 1, name_item)

    def clear_component(self):
        """Очистка таблицы компонентов"""
        self.ui.tableWidget_components.setRowCount(0)
    
    # =============================================================================
    # ОБРАБОТЧИКИ СОБЫТИЙ: УПРАВЛЕНИЕ
    # =============================================================================
    def on_create_task(self):
        """Открытие диалога создания задачи"""
        dialog = DialogCreateTask(self)
        if dialog.exec() == QDialog.Accepted:
            self.refresh_data()

    def on_delete_clicked(self):
        """Удаление задачи с подтверждением"""
        api_manager.api_task.delete_task(self.task['id'])
        self.refresh_data()

    def show_context_menu(self, pos):
        """Показать контекстное меню для изменения статуса задачи"""
        table = self.ui.tableWidget_tasks
        menu = QMenu(table)
        status_menu = QMenu("Изменить статус", menu)
        for status in api_manager.task_status:
            action = QAction(status['name'], status_menu)
            action.setCheckable(True)
            action.triggered.connect(lambda _, sid=status['id']: self.change_task_status(sid))
            status_menu.addAction(action)
        menu.addMenu(status_menu)
        menu.exec(table.viewport().mapToGlobal(pos))

    def change_task_status(self, status_id):
        """Изменить статус задачи через API"""
        api_manager.api_task.update_task_status(self.task['id'], status_id)
        self.refresh_data()

    def get_selected_row(self):
        """Возвращает выбранную задачу или None"""
        selected = self.ui.tableWidget_tasks.selectedItems()
        if selected:
            return selected[0].row()
        else:
            return None

    # =============================================================================
    # ОБРАБОТЧИКИ СОБЫТИЙ: ВЫДЕЛЕНИЕ И ПОИСК
    # =============================================================================
    def on_selection_changed(self):
        """Обработка выбора задачи"""
        self.selected_row = self.get_selected_row()
        if self.selected_row is not None:
            self.update_task_info_panel()
        else:
            self.selected_row = None
            self.clear_task_info_panel()

    def filter_table(self):
        """Фильтрация строк таблицы по первому столбцу"""
        table = self.ui.tableWidget_tasks
        text = self.ui.lineEdit_search.text().lower()
        for row in range(table.rowCount()):
            item = table.item(row, 0)
            visible = item and text in item.text().lower()
            table.setRowHidden(row, not visible)
    # =============================================================================
    # УПРАВЛЕНИЕ АВТООБНОВЛЕНИЕМ
    # =============================================================================
    def start_auto_refresh(self):
        """Запуск автообновления"""
        if not self.update_timer.isActive():
            self.update_timer.start(5000)
            self.refresh_data()

    def stop_auto_refresh(self):
        """Остановка автообновления"""
        if self.update_timer.isActive():
            self.update_timer.stop()