"""Содержимое задач для ADITIM Monitor Client"""
from PySide6.QtWidgets import QWidget, QTableWidgetItem, QAbstractItemView,  QMenu, QDialog
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
        self.load_ui()
        self.setup_ui()
        api_manager.data_updated.connect(self.refresh_data)

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
        # По умолчанию скрыть группу этапов работ
        self.ui.groupBox_component_stage.setVisible(False)
        # Настройка контекстного меню для таблицы задач
        self.ui.tableWidget_task.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.tableWidget_task.customContextMenuRequested.connect(self.show_context_menu)

        # Общие подключения
        self.ui.tabWidget_main.currentChanged.connect(self.refresh_data)
        # Подключение сигналов вкладки задач
        self.ui.pushButton_task_add.clicked.connect(self.on_create_task)
        self.ui.pushButton_task_delete.clicked.connect(self.on_delete_clicked)
        self.ui.tableWidget_task.itemClicked.connect(self.on_main_table_clicked)

        #подключение сигналов вкладки очереди
        self.ui.pushButton_position_up.clicked.connect(self.on_position_up_clicked)
        self.ui.pushButton_position_down.clicked.connect(self.on_position_down_clicked)
        self.ui.tableWidget_queue.itemClicked.connect(self.on_main_table_clicked)

        #подключение сигналов таблицы компонетов
        self.ui.tableWidget_component.itemClicked.connect(self.on_component_clicked)
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
        self.task = None
        self.clear_info_panel()
        if self.ui.tabWidget_main.currentIndex() == 0:
            self.ui.label_header.setText("ЗАДАЧИ")
            self.update_table_task()
        elif self.ui.tabWidget_main.currentIndex() == 1:
            self.ui.label_header.setText("ОЧЕРЕДЬ")
            self.update_table_queue()


    def update_table_task(self):
        """Обновление таблицы задач с корректным отображением и заполнением по ширине"""
        table = self.ui.tableWidget_task
        table.setRowCount(len(api_manager.table['task']))
        table.setColumnCount(8) 
        table.setHorizontalHeaderLabels(["№ задачи", "Название","Тип работ", "Статус", "Местоположение", "Срок", "Создано", "Описание"])

        for row, task in enumerate(api_manager.table['task']):
            item_number = QTableWidgetItem(f"Задача № {task['id']}")
            item_name = QTableWidgetItem(self.get_task_name(task))
            item_work_type = QTableWidgetItem(task['type']['name'])
            item_status = QTableWidgetItem(task['status']['name'])
            item_location = QTableWidgetItem(task['location']['name'])
            item_deadline = QTableWidgetItem(task['deadline'])
            item_created = QTableWidgetItem(task['created'])
            item_description = QTableWidgetItem(task['description'])

            item_number.setData(Qt.UserRole, task['id'])
            item_name.setData(Qt.UserRole, task['id'])
            item_work_type.setData(Qt.UserRole, task['id'])
            item_status.setData(Qt.UserRole, task['id'])
            item_location.setData(Qt.UserRole, task['id'])
            item_deadline.setData(Qt.UserRole, task['id'])
            item_created.setData(Qt.UserRole, task['id'])
            item_description.setData(Qt.UserRole, task['id'])

            table.setItem(row, 0, item_number)
            table.setItem(row, 1, item_name)
            table.setItem(row, 2, item_work_type)
            table.setItem(row, 3, item_status)
            table.setItem(row, 4, item_location)
            table.setItem(row, 5, item_deadline)
            table.setItem(row, 6, item_created)
            table.setItem(row, 7, item_description)

    def update_table_queue(self):
        """Обновление таблицы очереди с корректным отображением и заполнением по ширине"""
        table = self.ui.tableWidget_queue
        table.setRowCount(len(api_manager.table['queue']))
        table.setColumnCount(7) 
        # Заголовки столбцов
        table.setHorizontalHeaderLabels(["Позиция", "Название", "Тип работ", "Статус", "Срок", "Создано", "Описание"])
        for row, task in enumerate(api_manager.table['queue']):
            item_position = QTableWidgetItem(str(task['position']))
            item_name = QTableWidgetItem(self.get_task_name(task))
            item_work_type = QTableWidgetItem(task['type']['name'])
            item_status = QTableWidgetItem(task['status']['name'])
            item_deadline = QTableWidgetItem(task['deadline'])
            item_created = QTableWidgetItem(task['created'])
            item_description = QTableWidgetItem(task['description'])

            item_position.setData(Qt.UserRole, task['id'])
            item_name.setData(Qt.UserRole, task['id'])
            item_work_type.setData(Qt.UserRole, task['id'])
            item_status.setData(Qt.UserRole, task['id'])
            item_deadline.setData(Qt.UserRole, task['id'])
            item_created.setData(Qt.UserRole, task['id'])
            item_description.setData(Qt.UserRole, task['id'])

            table.setItem(row, 0, item_position)
            table.setItem(row, 1, item_name)
            table.setItem(row, 2, item_work_type)
            table.setItem(row, 3, item_status)
            table.setItem(row, 4, item_deadline)
            table.setItem(row, 5, item_created)
            table.setItem(row, 6, item_description)

    def update_task_info_panel(self):
        """Обновление панели информации о задаче"""
        self.ui.label_task_name.setText(self.task['type']['name'] + " - " + self.get_task_name(self.task))
        self.update_task_component_table()


    def update_queue_info_panel(self):
        """Обновление панели информации о задаче"""
        self.update_queue_component_table()

    def update_queue_component_table(self):
        """Обновление таблицы компонентов очереди"""
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

    def get_component_stage_status(self, component):
        """Определяет текущий статус этапа компонента
        
        Возвращает строку с текущим статусом:
        - "Название этапа" - если этап в процессе (есть start, нет finish)
        - "Ожидает: Название этапа" - если предыдущий завершён, текущий не начат
        - "Изготовлен" - если все этапы завершены
        """
        list_stage = component.get('stage', [])
        if not list_stage:
            return "Нет этапов"
        
        # Сортируем по номеру этапа
        sorted_stage = sorted(list_stage, key=lambda s: s.get('stage_num', 0))
        
        # Ищем последний этап с датой начала
        last_started_stage = None
        for stage in sorted_stage:
            if stage.get('start') and stage['start'] != 'None':
                last_started_stage = stage
        
        # Если есть начатый этап без окончания - текущий
        if last_started_stage and (not last_started_stage.get('finish') or last_started_stage['finish'] == 'None'):
            work_subtype = last_started_stage.get('work_subtype', {})
            return work_subtype.get('name', 'Неизвестный этап')
        
        # Ищем первый незавершённый этап
        for stage in sorted_stage:
            start = stage.get('start')
            finish = stage.get('finish')
            
            # Проверяем, что этап не начат или не завершён
            if not start or start == 'None' or not finish or finish == 'None':
                work_subtype = stage.get('work_subtype', {})
                stage_name = work_subtype.get('name', 'Неизвестный этап')
                
                # Если этап не начат - ожидает
                if not start or start == 'None':
                    return f"Ожидает: {stage_name}"
                # Если начат, но не завершён - текущий
                return stage_name
        
        # Все этапы завершены
        return "Изготовлен"

    def update_task_component_table(self):
        """Обновление таблицы компонентов задачи"""
        table = self.ui.tableWidget_component
        table.setRowCount(len(self.task['component']))
        
        # Проверяем по первому элементу, какой тип компонента
        if self.task['product_id']:
            table.setColumnCount(1)
            table.setHorizontalHeaderLabels(["Название"])
            for row, component in enumerate(self.task['component']):
                name_item = QTableWidgetItem(component['product_component']['name'])
                name_item.setData(Qt.UserRole, component)
                table.setItem(row, 0, name_item)
        elif self.task['profiletool_id']:
            if self.task['type_id'] == 0: 
                # тип задачи "Разработка"
                table.setColumnCount(2)
                table.setHorizontalHeaderLabels(["Название", "Статус"])
                for row, component in enumerate(self.task['component']):
                    # Название компонента
                    name_item = QTableWidgetItem(component['profiletool_component']['type']['name'])
                    name_item.setData(Qt.UserRole, component)
                    history = component['profiletool_component']['history']
                    if history:
                        last_history = history[-1]
                        if last_history['status']['id'] == 2:
                            status_name = last_history['status']['name']
                        else:
                            status_name = "Разработан"
                    else:
                        status_name = "Новая"
                        last_history = {"status": {"id": None, "name": "Нет истории"}}

                    status_item = QTableWidgetItem(status_name)
                    status_item.setData(Qt.UserRole, component)
                    table.setItem(row, 0, name_item)
                    table.setItem(row, 1, status_item)
            elif self.task['type_id'] == 1:
                # Тип задачи - "Изготовление"
                table.setColumnCount(2)
                table.setHorizontalHeaderLabels(["Название", "Этап"])
                for row, component in enumerate(self.task['component']):
                    name_item = QTableWidgetItem(component['profiletool_component']['type']['name'])
                    name_item.setData(Qt.UserRole, component)
                    
                    # Определяем текущий статус этапа
                    stage_status = self.get_component_stage_status(component)
                    stage_item = QTableWidgetItem(stage_status)
                    stage_item.setData(Qt.UserRole, component)
                    
                    table.setItem(row, 0, name_item)
                    table.setItem(row, 1, stage_item)
            elif self.task['type_id'] == 3:
                # Тип задачи - "Изготовление заготовок"
                table.setColumnCount(2)
                table.setHorizontalHeaderLabels(["Название", "Этап"])
                for row, component in enumerate(self.task['component']):
                    name_item = QTableWidgetItem(component['profiletool_component']['type']['name'])
                    name_item.setData(Qt.UserRole, component)
                    
                    # Определяем текущий статус этапа
                    stage_status = self.get_component_stage_status(component)
                    stage_item = QTableWidgetItem(stage_status)
                    stage_item.setData(Qt.UserRole, component)
                    
                    table.setItem(row, 0, name_item)
                    table.setItem(row, 1, stage_item)
                    
    def update_table_component_stage(self, component):
        """Заполняет tableWidget_component_stage этапами из выбранного компонента"""

        table = self.ui.tableWidget_component_stage
        table.setRowCount(len(component["stage"]))
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["№", "Операция", "Станок", "Начало", "Окончание"])

        for row, stage in enumerate(component["stage"]):
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

    def update_component_history(self, status, list_component):
        """Обновление истории компонентов задачи"""
        for component in list_component:
            profiletool_component_id = component['profiletool_component_id']
            api_manager.api_profiletool.create_profiletool_component_history(
                profiletool_component_id,  # ID из profiletool_component!
                {
                    "date": QDate.currentDate().toString("yyyy-MM-dd"),
                    "status_id": status,
                    "description": ""
                }
            )

    def get_task_name(self, task):
        """Возвращает название задачи: артикул профиля или имя изделия"""
        if task['profiletool_id']:
            profiletool = api_manager.get_by_id('profiletool', task['profiletool_id'])
            return f"Инструмент {profiletool['profile']['article']}"
        elif task['product_id']:
            product = api_manager.get_by_id('product', task['product_id'])
            return f"Изделие {product['name']}" if product else "Изделие N/A"

    def clear_info_panel(self):
        """Очистка таблицы компонентов"""
        self.ui.tableWidget_component.setRowCount(0)
        self.ui.tableWidget_component_stage.setRowCount(0)

    # =============================================================================
    # ОБРАБОТЧИКИ СОБЫТИЙ: ВЫДЕЛЕНИЕ
    # =============================================================================
    def on_main_table_clicked(self):
        """Обработчик выбора элемента"""
        if self.ui.tabWidget_main.currentIndex() == 0:
            self.task = api_manager.get_by_id("task", self.ui.tableWidget_task.currentItem().data(Qt.UserRole))
            self.update_task_info_panel()
        elif self.ui.tabWidget_main.currentIndex() == 1:
            self.task = api_manager.get_by_id("queue", self.ui.tableWidget_queue.currentItem().data(Qt.UserRole))
            self.update_task_info_panel()

    def on_component_clicked(self):
        """Обработка выбора компонента"""
        if self.task['type']['name'] == 'Разработка':
            self.ui.groupBox_component_stage.setVisible(False)
        else:
            self.ui.groupBox_component_stage.setVisible(True)
            self.update_table_component_stage(self.ui.tableWidget_component.currentItem().data(Qt.UserRole))

    # =============================================================================
    # ОБРАБОТЧИКИ СОБЫТИЙ: УПРАВЛЕНИЕ
    # =============================================================================
    def on_position_up_clicked(self):
        selected_row = self.ui.tableWidget_queue.currentRow()
        if selected_row <= 0:
            return
        # Получаем ID задачи из таблицы (колонка 0 — ID)
        current_task_id = self.ui.tableWidget_queue.item(selected_row, 0).data(Qt.UserRole)
        # Теперь получаем ПОЛНЫЙ список ID задач в порядке очереди
        task_ids = [task['id'] for task in api_manager.table['queue']]
        try:
            # Находим индекс задачи в api_manager.queue (не в таблице!)
            current_idx_in_list = next(i for i, tid in enumerate(task_ids) if tid == current_task_id)
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

    def on_position_down_clicked(self):
        """Переместить задачу вниз"""
        selected_row = self.ui.tableWidget_queue.currentRow()
        if selected_row == -1:
            return
        # Получаем ID задачи из текущей строки (колонка 0 — ID)
        current_task_id = self.ui.tableWidget_queue.item(selected_row, 0).data(Qt.UserRole)
        # Получаем текущий порядок задач в очереди (в статусе "В работе")
        task_ids = [task['id'] for task in api_manager.table['queue']]
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

    def on_create_task(self):
        """Открытие диалога создания задачи"""
        wizard = WizardTaskCreate(self)
        if wizard.exec() == QDialog.Accepted:
            QMessageBox.warning(self, "Внимание", "Задача создана")

    def on_delete_clicked(self):
        """Удаление задачи с подтверждением"""
        if self.task:
            api_manager.api_task.delete_task(self.task['id'])
            QMessageBox.warning(self, "Внимание", "Задача удалена")
        else:
            QMessageBox.warning(self, "Внимание", "Выберите задачу для удаления")

    def show_context_menu(self, pos):
        """Показать контекстное меню для изменения статуса задачи"""
        table = self.ui.tableWidget_task
        menu = QMenu(table)
        status_menu = QMenu("Изменить статус", menu)
        location_menu = QMenu("Изменить местоположение", menu)
        for status in api_manager.directory['task_status']:
            # Проверяем, нужно ли добавлять этот статус в меню
            current_status_name = self.task['status']['name']
            status_name = status['name']
            if status['id'] == self.task['status']['id']:
                continue  # Уже установлен — не добавлять
            if current_status_name == "В работе" and status_name == "Новая":
                continue  # Не добавлять "Новая" если уже "В работе"
            if current_status_name == "Выполнена" and status_name in ("В работе", "Новая"):
                continue  # Не добавлять "В работе" и "Новая" если уже "Выполнена"
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
        # Проверка: если выбранный статус совпадает с текущим, ничего не делать
        if self.task['status']['id'] == status_id:
            return
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
            status = 2 # В разработке
            self.update_component_history(status, task['component'])
        elif task['type']['name'] == 'Изготовление' and task['status']['name'] == 'В работе':
            status = 4 # Изготовление
            self.update_component_history(status, task['component'])
        elif task['type']['name'] == 'Заготовка' and task['status']['name'] == 'В работе':
            status = 11 # Изготовление
            self.update_component_history(status, task['component'])
        

    def change_task_location(self, location_id):
        api_manager.api_task.update_task_location(self.task['id'], location_id)
