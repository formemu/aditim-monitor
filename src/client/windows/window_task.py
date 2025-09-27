"""Содержимое задач для ADITIM Monitor Client"""
from PySide6.QtWidgets import QWidget, QTableWidgetItem, QAbstractItemView,  QMenu, QHeaderView
from PySide6.QtCore import QFile, Qt, QDate
from PySide6.QtGui import QAction, QPixmap
from PySide6.QtUiTools import QUiLoader
from ..constant import UI_PATHS_ABS, ICON_PATHS_ABS, get_style_path
from ..widgets.wizard_task_create.wizard_task_create import WizardTaskCreate
from ..style_util import load_styles
from ..api_manager import api_manager
from PySide6.QtWidgets import QMessageBox


class WindowTask(QWidget):
    """Виджет содержимого задач"""
    def __init__(self):
        super().__init__()
        self.task = None
        self.component = None
        self.tab_index = 0  # Индекс текущей вкладки
        self.selected_row = None
        self.selected_component_row = None
        self.load_ui()
        self.setup_ui()
        self.connect_signals()

    # =============================================================================
    # ИНИЦИАЛИЗАЦИЯ И ЗАГРУЗКА ИНТЕРФЕЙСА
    # =============================================================================
    def load_ui(self):
        """Загрузка UI из файла"""
        ui_file = QFile(UI_PATHS_ABS["TASK_CONTENT"])
        ui_file.open(QFile.ReadOnly)
        loader = QUiLoader()
        self.ui = loader.load(ui_file)
        ui_file.close()
        

    def setup_ui(self):
        """Настройка UI компонентов"""
        self.ui.setStyleSheet(load_styles(get_style_path("MAIN")))
        self.load_logo()
        # Настройка контекстного меню для таблицы задач
        self.ui.tableWidget_task.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.tableWidget_task.customContextMenuRequested.connect(self.show_context_menu)

        # Общие подключения
        self.ui.tabWidget_main.currentChanged.connect(self.on_tab_changed)
        # Подключение сигналов вкладки задач
        self.ui.pushButton_task_add.clicked.connect(self.on_create_task)
        self.ui.pushButton_task_delete.clicked.connect(self.on_delete_clicked)
        self.ui.tableWidget_task.itemSelectionChanged.connect(self.on_selection_changed)

        #подключение сигналов вкладки очереди
        self.ui.pushButton_position_up.clicked.connect(self.on_position_up_clicked)
        self.ui.pushButton_position_down.clicked.connect(self.on_position_down_clicked)
        self.ui.tableWidget_queue.itemSelectionChanged.connect(self.on_selection_changed)

        #подключение сигналов таблицы компонетов
        self.ui.tableWidget_component.itemSelectionChanged.connect(self.on_selection_component_changed)
        # Настройка таблицы задач
        table = self.ui.tableWidget_task
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setSelectionMode(QAbstractItemView.SingleSelection)
        table.setFocusPolicy(Qt.NoFocus)
        self.refresh_data()

    def load_logo(self):
        """Загрузка логотипа ADITIM"""
        logo_path = ICON_PATHS_ABS.get("ADITIM_LOGO_MAIN")
        pixmap = QPixmap(logo_path)
        scaled = pixmap.scaled(300, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.ui.label_logo.setPixmap(scaled)
        self.ui.label_logo.setText("")
    # =============================================================================
    # УПРАВЛЕНИЕ ДАННЫМИ: ЗАГРУЗКА И ОБНОВЛЕНИЕ
    # =============================================================================
    def refresh_data(self):
        """Принудительное обновление данных"""
        if self.tab_index == 0:
            self.update_table_task()
        elif self.tab_index == 1:
            self.update_table_queue()

    def connect_signals(self):
        """Подключаемся к сигналам ApiManager"""
        api_manager.data_updated.connect(self.on_data_updated)

    def on_data_updated(self, group: str, key: str, success: bool):
        """Реакция на обновление данных"""
        if success and group == "table" and key == "task":
            self.update_table_task()
        elif success and group == "table" and key == "queue":
            self.update_table_queue()

    def on_tab_changed(self):
        """Обработчик смены вкладки — обновляет данные для выбранной вкладки"""
        self.tab_index = self.ui.tabWidget_main.currentIndex()
        if self.tab_index == 0:
            self.ui.label_header.setText("ЗАДАЧИ")
        elif self.tab_index == 1:
            self.ui.label_header.setText("ОЧЕРЕДЬ")
        self.clear_component()
        self.selected_row = 0
        self.refresh_data()

    # =============================================================================
    # ОТОБРАЖЕНИЕ ДАННЫХ: ТАБЛИЦЫ И ИНФОРМАЦИОННЫЕ ПАНЕЛИ
    # =============================================================================
    def update_table_task(self):
        """Обновление таблицы задач с корректным отображением и заполнением по ширине"""
        table = self.ui.tableWidget_task
        table.setRowCount(len(api_manager.table['task']))
        table.setColumnCount(8) 
        # Заголовки столбцов
        table.setHorizontalHeaderLabels(["№ задачи", "Название","Тип работ", "Статус", "Местоположение", "Срок", "Создано", "Описание"])
        header = table.horizontalHeader()
        for col in range(table.columnCount() - 1):
            header.setSectionResizeMode(col, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(table.columnCount() - 1, QHeaderView.Stretch)
        for row, task in enumerate(api_manager.table['task']):
            item_number = QTableWidgetItem(f"Задача № {task['id']}")
            item_number.setData(Qt.UserRole, task['id'])
            table.setItem(row, 0, item_number)
            name = self.get_task_name(task)
            table.setItem(row, 1, QTableWidgetItem(name))
            work_type = task['type']['name']
            table.setItem(row, 2, QTableWidgetItem(work_type))
            status = task['status']['name']
            table.setItem(row, 3, QTableWidgetItem(status))
            location = task['location']['name']
            table.setItem(row, 4, QTableWidgetItem(location))
            deadline = task['deadline']
            table.setItem(row, 5, QTableWidgetItem(deadline))
            created = task['created']
            table.setItem(row, 6, QTableWidgetItem(created))
            description = task['description']
            table.setItem(row, 7, QTableWidgetItem(description))


    def update_table_queue(self):
        """Обновление таблицы очереди с корректным отображением и заполнением по ширине"""
        table = self.ui.tableWidget_queue
        table.setRowCount(len(api_manager.table['queue']))
        table.setColumnCount(7) 
        # Заголовки столбцов
        table.setHorizontalHeaderLabels(["Позиция", "Название", "Тип работ", "Статус", "Срок", "Создано", "Описание"])
        header = table.horizontalHeader()
        for col in range(table.columnCount() - 1):
            header.setSectionResizeMode(col, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(table.columnCount() - 1, QHeaderView.Stretch)
        for row, task in enumerate(api_manager.table['queue']):
            item_position = QTableWidgetItem(str(task['position']))
            item_position.setData(Qt.UserRole, task['id'])
            table.setItem(row, 0, item_position)
            name = self.get_task_name(task)
            table.setItem(row, 1, QTableWidgetItem(name))
            work_type = task['type']['name']
            table.setItem(row, 2, QTableWidgetItem(work_type))
            status = task['status']['name']
            table.setItem(row, 3, QTableWidgetItem(status))
            deadline = task['deadline']
            table.setItem(row, 4, QTableWidgetItem(deadline))
            created = task['created']
            table.setItem(row, 5, QTableWidgetItem(created))
            description = task['description']
            table.setItem(row, 6, QTableWidgetItem(description))

    def update_task_info_panel(self):
        """Обновление панели информации о задаче"""
        if self.task is not None:
            name = self.get_task_name(self.task)
            deadline = self.task['deadline']
            created = self.task['created']
            status = self.task['status']['name']
            self.ui.label_task_name.setText(f"Название: {name}")
            self.ui.label_task_info.setText(f"Статус: {status} | Срок: {deadline} | Создано: {created}")
            self.load_component()
        else:
            self.clear_task_info_panel()

    def get_task_name(self, task):
        """Возвращает название задачи: артикул профиля или имя изделия"""
        if task['profiletool_id']:
            profiletool = api_manager.get_by_id('profiletool', task['profiletool_id'])
            return f"Инструмент {profiletool['profile']['article']}"
        elif task['product_id']:
            product = api_manager.get_by_id('product', task['product_id'])
            return f"Изделие {product['name']}" if product else "Изделие N/A"

    def clear_task_info_panel(self):
        """Очистка панели задачи"""
        self.ui.label_task_name.setText("Название: -")
        self.ui.label_task_info.setText("Статус: - | Срок: - | Создано: -")
        self.clear_component()

    def load_component(self):
        """Обновление таблицы компонентов"""
        table = self.ui.tableWidget_component
        table.setRowCount(len(self.task['component']))
        # Проверяем по первому элементу, какой тип компонента
        if self.task['component'] and self.task['component'][0]['product_component_id']:
            table.setColumnCount(1)
            table.setHorizontalHeaderLabels(["№", "Название"])
            for row, component in enumerate(self.task['component']):
                name_item = QTableWidgetItem(component['product_component']['name'])
                name_item.setData(Qt.UserRole, component['id'])
                table.setItem(row, 0, name_item)
        else:
            table.setColumnCount(1)
            table.setHorizontalHeaderLabels(["№", "Название"])
            for row, component in enumerate(self.task['component']):
                name_item = QTableWidgetItem(component['profiletool_component']['type']['name'])
                name_item.setData(Qt.UserRole, component['id'])
                table.setItem(row, 0, name_item)

    def clear_component(self):
        """Очистка таблицы компонентов"""
        self.ui.tableWidget_component.setRowCount(0)
    
    # =============================================================================
    # ОБРАБОТЧИКИ СОБЫТИЙ: УПРАВЛЕНИЕ
    # =============================================================================
    def on_position_up_clicked(self):
        selected_row = self.ui.tableWidget_queue.currentRow()
        if selected_row <= 0:
            return
        # Получаем ID задачи из таблицы (колонка 0 — ID)
        item = self.ui.tableWidget_queue.item(selected_row, 0)
        if not item:
            return
        current_task_id = int(item.text())
        # Теперь получаем ПОЛНЫЙ список ID задач в порядке очереди
        task_ids = [task['id'] for task in api_manager.queue]
        try:
            # Находим индекс задачи в api_manager.queue (не в таблице!)
            current_idx_in_list = next(i for i, t in enumerate(task_ids) if t == current_task_id)
        except StopIteration:
            return  # Задача не найдена в списке
        if current_idx_in_list == 0:
            return  # Уже на верху
        # Меняем местами в списке
        above_idx = current_idx_in_list - 1
        task_ids[current_idx_in_list], task_ids[above_idx] = task_ids[above_idx], task_ids[current_idx_in_list]
        # Отправляем
        api_manager.api_task.reorder_task_queue(task_ids)
        # Обновляем
        self.refresh_data()
        # Выделяем перемещённую задачу
        self.select_row_by_task_id(current_task_id)

    def on_position_down_clicked(self):
        """Переместить задачу вниз"""
        selected_row = self.ui.tableWidget_queue.currentRow()
        if selected_row == -1:
            return
        # Получаем ID задачи из текущей строки (колонка 0 — ID)
        item = self.ui.tableWidget_queue.item(selected_row, 0)
        if not item:
            return
        current_task_id = int(item.text())
        # Получаем текущий порядок задач в очереди (в статусе "В работе")
        task_ids = [task['id'] for task in api_manager.queue]
        # Находим индекс задачи в списке api_manager.queue (не в таблице!)
        try:
            current_idx_in_list = next(i for i, tid in enumerate(task_ids) if tid == current_task_id)
        except StopIteration:
            return  # Задача не найдена в списке — возможно, данные устарели
        # Проверяем: можно ли переместить вниз?
        if current_idx_in_list >= len(task_ids) - 1:
            return  # Уже последняя
        # Меняем местами с нижестоящей задачей
        below_idx = current_idx_in_list + 1
        task_ids[current_idx_in_list], task_ids[below_idx] = task_ids[below_idx], task_ids[current_idx_in_list]
        # Отправляем обновлённый порядок на сервер
        api_manager.api_task.reorder_task_queue(task_ids)
        # Обновляем интерфейс
        self.refresh_data()
        # Восстанавливаем выделение на перемещённой задаче
        self.select_row_by_task_id(current_task_id)

    def select_row_by_task_id(self, task_id):
        """Находит строку по ID задачи и выделяет её"""
        table = self.ui.tableWidget_queue
        for row in range(table.rowCount()):
            item = table.item(row, 0)  # Колонка 0 — ID
            if item and item.text() == str(task_id):
                table.selectRow(row)
                table.scrollToItem(item, QAbstractItemView.PositionAtCenter)
                return

    def on_create_task(self):
        """Открытие диалога создания задачи"""
        # dialog = DialogCreateTask(self)
        # if dialog.exec() == QDialog.Accepted:
        #     self.refresh_data()
        wizard = WizardTaskCreate(self)
        wizard.exec()

    def on_delete_clicked(self):
        """Удаление задачи с подтверждением"""
        api_manager.api_task.delete_task(self.task['id'])

    def show_context_menu(self, pos):
        """Показать контекстное меню для изменения статуса задачи"""
        table = self.ui.tableWidget_task
        menu = QMenu(table)
        status_menu = QMenu("Изменить статус", menu)
        location_menu = QMenu("Изменить местоположение", menu)
        for status in api_manager.directory['task_status']:
            action = QAction(status['name'], status_menu)
            action.setCheckable(True)
            action.triggered.connect(lambda _, status_id=status['id']: self.change_task_status(status_id))
            status_menu.addAction(action)
        menu.addMenu(status_menu)
        for location in api_manager.directory['task_location']:
            action = QAction(location['name'], location_menu)
            action.setCheckable(True)
            action.triggered.connect(lambda _, location_id=location['id']: self.change_task_location(location_id))
            location_menu.addAction(action)
        menu.addMenu(location_menu)

        menu.exec(table.viewport().mapToGlobal(pos))

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

    def change_task_location(self, location_id):
        api_manager.api_task.update_task_location(self.task['id'], location_id)


    # =============================================================================
    # ОБРАБОТЧИКИ СОБЫТИЙ: ВЫДЕЛЕНИЕ И ПОИСК
    # =============================================================================
    def on_selection_changed(self):
        """Обработка выбора задачи"""
        if self.tab_index == 0:
            self.selected_row = self.ui.tableWidget_task.currentRow()
            id = self.ui.tableWidget_task.item(self.selected_row, 0).data(Qt.UserRole)
            if id:
                self.task = api_manager.get_by_id('task', id)
            else:
                self.task = None
                self.selected_row = None
        elif self.tab_index == 1:
            self.selected_row = self.ui.tableWidget_queue.currentRow()
            id = self.ui.tableWidget_queue.item(self.selected_row, 0).data(Qt.UserRole)
            if id:
                self.task = api_manager.get_by_id('task', id)
        self.update_task_info_panel()

    def on_selection_component_changed(self):
        """Обработка выбора компонента"""
        self.selected_component_row = self.ui.tableWidget_component.currentRow()
        id = self.ui.tableWidget_component.item(self.selected_component_row, 0).data(Qt.UserRole)
        component_id = id
        self.component = api_manager.find_in(self.task, "component", id=component_id)[0]
        self.update_table_component_stage()

    def update_table_component_stage(self):
        """Заполняет tableWidget_component_stage этапами из выбранного компонента"""
        if not self.component["stage"]:
            return
        table = self.ui.tableWidget_component_stage
        table.setRowCount(len(self.component["stage"]))
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["№", "Операция", "Станок", "Начало", "Окончание"])
        

        for row, stage in enumerate(self.component["stage"]):
            # Порядковый номер
            stage_num = str(stage["stage_num"])
            item_stage_num = QTableWidgetItem(stage_num)
            item_stage_num.setData(Qt.UserRole, stage["id"])
            self.ui.tableWidget_component_stage.setItem(row, 0, item_stage_num)

            # Название операции
            work_subtype = stage["work_subtype"]
            work_name = work_subtype["name"] if work_subtype else "Без типа"
            work_item = QTableWidgetItem(work_name)
            self.ui.tableWidget_component_stage.setItem(row, 1, work_item)

            # Станок
            machine = stage["machine"]
            machine_name = machine["name"] if machine else ""
            item_machine = QTableWidgetItem(machine_name)
            self.ui.tableWidget_component_stage.setItem(row, 2, item_machine)

            # Дата начала
            start = stage["start"]
            item_start = QTableWidgetItem(start)
            self.ui.tableWidget_component_stage.setItem(row, 3, item_start)

            # Дата окончания
            finish = stage["finish"]
            item_finish = QTableWidgetItem(finish)
            self.ui.tableWidget_component_stage.setItem(row, 4, item_finish)


    # =============================================================================
    # ОКНО ПРЕДУПРЕЖДЕНИЯ
    # =============================================================================
    def show_warning_dialog(self, message: str):
        """Показать окно предупреждения с заданным сообщением"""
        QMessageBox.warning(self, "Внимание", message)