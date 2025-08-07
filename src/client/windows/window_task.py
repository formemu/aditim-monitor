"""
Содержимое задач для ADITIM Monitor Client
"""
from PySide6.QtWidgets import QWidget, QMessageBox, QTableWidgetItem, QAbstractItemView,  QMenu, QHeaderView
from PySide6.QtCore import QFile, Qt, QTimer
from PySide6.QtGui import QAction
from PySide6.QtUiTools import QUiLoader
from datetime import datetime
from ..constant import UI_PATHS_ABS as UI_PATHS, get_style_path
from ..widgets.dialog_create_task import DialogCreateTask
from ..api.api_task import ApiTask
from ..style_util import load_styles
from ..references_manager import references_manager


class WindowTask(QWidget):
    """Виджет содержимого задач"""
    def __init__(self):
        super().__init__()
        self.api_task = ApiTask()
        self.task_data = None  # Кэш задач
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
        self.ui.pushButton_task_edit.clicked.connect(self.on_edit_clicked)
        self.ui.pushButton_task_delete.clicked.connect(self.on_delete_clicked)
        self.ui.tableWidget_tasks.itemSelectionChanged.connect(self.on_selection_changed)
        self.ui.lineEdit_search.textChanged.connect(lambda text: self.filter_table(self.ui.tableWidget_tasks, text.lower()))
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
        self.task_data = []
        self.dict_task_position = {}
        self.load_data_from_server()
        self.create_dict_task_position()

    def load_data_from_server(self):
        """Загрузка задач с сервера"""
        task = self.api_task.get_task()
        if self.skip_update(self.task_data, task):
            return
        self.task_data = task
        self.update_task_table(self.task_data)

    def create_dict_task_position(self):
        """Формирует словарь: задача_id -> позиция"""
        if not self.task_data:
            return {}
        self.dict_task_position = {}
        for task in self.task_data:
            self.dict_task_position[task.get('id')] = task.get('position')
        return self.dict_task_position
    
    # =============================================================================
    # ОТОБРАЖЕНИЕ ДАННЫХ: ТАБЛИЦЫ И ИНФОРМАЦИОННЫЕ ПАНЕЛИ
    # =============================================================================
    def update_task_table(self, list_task):
        """Обновление таблицы задач с корректным отображением и заполнением по ширине"""
        table = self.ui.tableWidget_tasks
        table.setRowCount(len(list_task))
        table.setColumnCount(6) 

        # Заголовки столбцов
        table.setHorizontalHeaderLabels([
            "Название", "Статус", "Позиция", "Срок", "Создано", "Описание"
        ])

        header = table.horizontalHeader()
        
        for col in range(table.columnCount() - 1):
            header.setSectionResizeMode(col, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(table.columnCount() - 1, QHeaderView.Stretch)
        for row, task in enumerate(list_task):
            # Название задачи
            name = self.get_task_name(task)
            table.setItem(row, 0, QTableWidgetItem(name))

            # Статус
            status = task.get('status')
            table.setItem(row, 1, QTableWidgetItem(status))

            # Позиция
            position = str(task.get('position'))
            table.setItem(row, 2, QTableWidgetItem(position))

            # Срок
            deadline = task.get('deadline_on')
            table.setItem(row, 3, QTableWidgetItem(deadline))

            # Дата создания
            created = task.get('created_at')
            table.setItem(row, 4, QTableWidgetItem(created))
            # Описание
            description = task.get('description')
            table.setItem(row, 5, QTableWidgetItem(description))

    def skip_update(self, current_data, new_data):
        """Проверка, нужно ли обновлять таблицу"""
        is_table_empty = self.ui.tableWidget_tasks.rowCount() == 0
        # Если таблица пуста — всегда обновляем
        if is_table_empty:
            return False
        # Если данные не изменились и таблица не пуста — пропускаем обновление
        if current_data is not None and new_data == current_data:
            return True
        # В остальных случаях — обновляем
        return False

    def get_task_name(self, task):
        """Возвращает название задачи: артикул профиля или имя изделия"""
        if task.get('profile_tool_id'):
            profile_tool = references_manager.get_profile_tool().get(task['profile_tool_id'])
            return f"Инструмент {profile_tool['name']}"
        product = references_manager.get_product().get(task.get('product_id'))
        return f"Изделие {product['name']}" if product else "Изделие N/A"

    def update_info_panel(self, task):
        """Обновление панели информации о задаче"""
        name = self.get_task_name(task)
        deadline = task.get('deadline_on')
        created = task.get('created_at')
        status = task.get('status')
        self.ui.label_task_name.setText(f"Название: {name}")
        self.ui.label_task_info.setText(f"Статус: {status} | Срок: {deadline} | Создано: {created}")

    def clear_info_panel(self):
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
        dialog.task_created.connect(self.refresh_data)
        dialog.exec()

    def on_edit_clicked(self):
        """Редактирование задачи"""
        if not self.get_selected_row():
            QMessageBox.warning(self, "Редактирование", "Выберите задачу для редактирования.")
        else:
            QMessageBox.information(self, "Редактировать", "Функция будет реализована позже")

    def on_delete_clicked(self):
        """Удаление задачи с подтверждением"""
        row = self.get_selected_row()
        task = self.task_data[row]
        self.api_task.delete_task(task['id'])
        self.refresh_data()

    def get_selected_row(self):
        """Возвращает индекс выбранной строки или None"""
        selected = self.ui.tableWidget_tasks.selectedItems()
        return selected[0].row() if selected else None

    def show_context_menu(self, pos):
        """Показать контекстное меню для изменения статуса задачи"""
        table = self.ui.tableWidget_tasks
        index = table.indexAt(pos)
        if not index.isValid():
            return

        row = index.row()
        task = self.task_data[row]
        status_dict = references_manager.get_task_status()

        menu = QMenu(table)
        status_menu = QMenu("Изменить статус", menu)

        current_status_id = task.get('task_status_id')
        for status_id, status_name in status_dict.items():
            action = QAction(status_name, status_menu)
            action.setCheckable(True)
            action.setChecked(status_id == current_status_id)
            action.triggered.connect(lambda checked, sid=status_id, r=row: self.change_task_status(r, sid))
            status_menu.addAction(action)

        menu.addMenu(status_menu)
        menu.exec(table.viewport().mapToGlobal(pos))

    def change_task_status(self, row, status_id):
        """Изменить статус задачи через API"""
        task = self.task_data[row]
        try:
            self.api_task.update_task_status(task['id'], status_id)
            self.refresh_data()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось изменить статус: {e}")
    
    # =============================================================================
    # ОБРАБОТЧИКИ СОБЫТИЙ: ВЫДЕЛЕНИЕ И ПОИСК
    # =============================================================================
    def on_selection_changed(self):
        """Обработка выбора задачи"""
        row = self.get_selected_row()
        if row is not None:
            task = self.task_data[row]
            self.update_info_panel(task)
            self.load_component(task['id'])
        else:
            self.clear_info_panel()
            self.clear_component()

    def filter_table(self, table, text):
        """Фильтрация строк таблицы по первому столбцу"""
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
            self.load_data_from_server()

    def stop_auto_refresh(self):
        """Остановка автообновления"""
        if self.update_timer.isActive():
            self.update_timer.stop()