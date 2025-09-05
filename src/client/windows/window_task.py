"""Содержимое задач для ADITIM Monitor Client"""
from PySide6.QtWidgets import QWidget, QTableWidgetItem, QAbstractItemView,  QMenu, QHeaderView, QDialog, QWizard
from PySide6.QtCore import QFile, Qt, QTimer
from PySide6.QtGui import QAction
from PySide6.QtUiTools import QUiLoader
from ..constant import UI_PATHS_ABS as UI_PATHS, get_style_path
from ..widgets.wizard_task_create import WizardTaskCreate
from ..style_util import load_styles
from ..api_manager import api_manager


class WindowTask(QWidget):
    """Виджет содержимого задач"""
    def __init__(self):
        super().__init__()
        self.task = None
        self.tab_index = 0  # Индекс текущей вкладки
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

        # Общие подключения
        self.ui.tabWidget_tasks.currentChanged.connect(self.on_tab_changed)
        # Подключение сигналов вкладки задач
        self.ui.pushButton_task_add.clicked.connect(self.on_create_task)
        self.ui.pushButton_task_delete.clicked.connect(self.on_delete_clicked)
        self.ui.tableWidget_tasks.itemSelectionChanged.connect(self.on_selection_changed)

        #подключение сигналов вкладки очереди
        self.ui.pushButton_position_up.clicked.connect(self.on_position_up_clicked)
        self.ui.pushButton_position_down.clicked.connect(self.on_position_down_clicked)
        self.ui.tableWidget_queue.itemSelectionChanged.connect(self.on_selection_changed)
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
        if self.tab_index == 0:
            api_manager.load_task()
            self.update_task_table()
        elif self.tab_index == 1:
            api_manager.load_queue()
            self.update_queue_table()
    
    def on_tab_changed(self):
        """Обработчик смены вкладки — обновляет данные для выбранной вкладки"""
        self.tab_index = self.ui.tabWidget_tasks.currentIndex()
        self.clear_component()
        self.selected_row = 0
        self.refresh_data()

    # =============================================================================
    # ОТОБРАЖЕНИЕ ДАННЫХ: ТАБЛИЦЫ И ИНФОРМАЦИОННЫЕ ПАНЕЛИ
    # =============================================================================
    def update_task_table(self):
        """Обновление таблицы задач с корректным отображением и заполнением по ширине"""
        table = self.ui.tableWidget_tasks
        table.setRowCount(len(api_manager.task))
        table.setColumnCount(7) 
        # Заголовки столбцов
        table.setHorizontalHeaderLabels(["id", "№ задачи", "Название", "Статус", "Срок", "Создано", "Описание"])
        header = table.horizontalHeader()
        for col in range(table.columnCount() - 1):
            header.setSectionResizeMode(col, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(table.columnCount() - 1, QHeaderView.Stretch)
        for row, task in enumerate(api_manager.task):
            id = task['id']
            table.setItem(row, 0, QTableWidgetItem(str(id)))
            table.setItem(row, 1, QTableWidgetItem(f"Задача № {id}"))
            name = self.get_task_name(task)
            table.setItem(row, 2, QTableWidgetItem(name))
            status = task['status']['name']
            table.setItem(row, 3, QTableWidgetItem(status))
            deadline = task['deadline']
            table.setItem(row, 4, QTableWidgetItem(deadline))
            created = task['created']
            table.setItem(row, 5, QTableWidgetItem(created))
            description = task['description']
            table.setItem(row, 6, QTableWidgetItem(description))
        table.setColumnHidden(0, True)  

    def update_queue_table(self):
        """Обновление таблицы очереди с корректным отображением и заполнением по ширине"""
        table = self.ui.tableWidget_queue
        table.setRowCount(len(api_manager.queue))
        table.setColumnCount(7) 
        # Заголовки столбцов
        table.setHorizontalHeaderLabels(["id", "Позиция", "Название", "Статус", "Срок", "Создано", "Описание"])
        header = table.horizontalHeader()
        for col in range(table.columnCount() - 1):
            header.setSectionResizeMode(col, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(table.columnCount() - 1, QHeaderView.Stretch)
        for row, task in enumerate(api_manager.queue):
            id = task['id']

            table.setItem(row, 0, QTableWidgetItem(str(id)))
            position = task['position']
            table.setItem(row, 1, QTableWidgetItem(str(position)))
            name = self.get_task_name(task)
            table.setItem(row, 2, QTableWidgetItem(name))
            status = task['status']['name']
            table.setItem(row, 3, QTableWidgetItem(status))
            deadline = task['deadline']
            table.setItem(row, 4, QTableWidgetItem(deadline))
            created = task['created']
            table.setItem(row, 5, QTableWidgetItem(created))
            description = task['description']
            table.setItem(row, 6, QTableWidgetItem(description))    
        table.setColumnHidden(0, True)  

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
        self.clear_component()

    def load_component(self):
        """Загрузка компонентов задачи по её идентификатору. """
        """Обновление таблицы компонентов"""
        table = self.ui.tableWidget_components
        table.setRowCount(len(self.task['component']))

        # Проверяем по первому элементу, какой тип компонента
        print(self.task)
        if self.task['component'] and self.task['component'][0]['product_component_id']:
            table.setColumnCount(2)
            header = table.horizontalHeader()
            header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(1, QHeaderView.Stretch)
            table.setHorizontalHeaderLabels(["№", "Название"])
            for row, comp in enumerate(self.task['component']):
                num_item = QTableWidgetItem(str(row + 1))
                table.setItem(row, 0, num_item)
                name_item = QTableWidgetItem(comp['product_component']['name'])
                table.setItem(row, 1, name_item)
        else:
            table.setColumnCount(2)
            header = table.horizontalHeader()
            header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(1, QHeaderView.Stretch)
            table.setHorizontalHeaderLabels(["№", "Название"])
            for row, comp in enumerate(self.task['component']):
                num_item = QTableWidgetItem(str(row + 1))
                table.setItem(row, 0, num_item)
                type_item = QTableWidgetItem(comp['profile_tool_component']['type']['name'])
                table.setItem(row, 1, type_item)

    def clear_component(self):
        """Очистка таблицы компонентов"""
        self.ui.tableWidget_components.setRowCount(0)
    
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
        if wizard.exec() == QWizard.Accepted:
            self.refresh_data()

    def on_delete_clicked(self):
        """Удаление задачи с подтверждением"""
        api_manager.api_task.delete_task(self.task['id'])
        if self.ui.tableWidget_tasks.rowCount() > 0:
            item = self.ui.tableWidget_tasks.item(0, 0)
            if item is not None:
                self.ui.tableWidget_tasks.setCurrentItem(item)
                self.selected_row = 0
        else:
            self.selected_row = None
        self.refresh_data()

    def show_context_menu(self, pos):
        """Показать контекстное меню для изменения статуса задачи"""
        table = self.ui.tableWidget_tasks
        menu = QMenu(table)
        status_menu = QMenu("Изменить статус", menu)
        for status in api_manager.task_status:
            action = QAction(status['name'], status_menu)
            action.setCheckable(True)
            action.triggered.connect(lambda _, status_id=status['id']: self.change_task_status(status_id))
            status_menu.addAction(action)
        menu.addMenu(status_menu)
        menu.exec(table.viewport().mapToGlobal(pos))

    def change_task_status(self, status_id):
        # 1. Обновить статус
        task = api_manager.api_task.update_task_status(self.task['id'], status_id)

        # 2. Получить ВСЕ задачи в статусе "В работе"
        queue = api_manager.api_task.get_queue() or []
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
            

        
        self.refresh_data()

    # =============================================================================
    # ОБРАБОТЧИКИ СОБЫТИЙ: ВЫДЕЛЕНИЕ И ПОИСК
    # =============================================================================
    def on_selection_changed(self):
        """Обработка выбора задачи"""
        if self.tab_index == 0:
            row = self.ui.tableWidget_tasks.currentRow()
            if row >= 0:
                self.selected_row = row
                item = self.ui.tableWidget_tasks.item(row, 0)
                if item is not None:
                    task_id = item.text()
                    self.task = api_manager.get_task_by_id(task_id)
                    self.selected_row = row
                else:
                    self.task = None
                    self.selected_row = None
            else:
                self.task = None
                self.selected_row = None

            self.update_task_info_panel()

        elif self.tab_index == 1:
            row = self.ui.tableWidget_queue.currentRow()
            if row >= 0:
                self.selected_row = row
                item = self.ui.tableWidget_queue.item(row, 0)
                if item:
                    task_id = item.text()
                    self.task = api_manager.get_task_by_id(task_id)
            else:
                self.selected_row = None
                self.task = None

            self.update_task_info_panel()

        else:
            self.selected_row = None
            self.task = None
            self.update_task_info_panel()
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