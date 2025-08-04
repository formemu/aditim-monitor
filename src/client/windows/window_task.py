"""
Содержимое задач для ADITIM Monitor Client
"""
from PySide6.QtWidgets import QWidget, QMessageBox, QTableWidgetItem, QAbstractItemView,  QMenu
from PySide6.QtCore import QFile, Qt, QTimer
from PySide6.QtGui import QAction
from PySide6.QtUiTools import QUiLoader
from datetime import datetime
from ..constant import UI_PATHS_ABS as UI_PATHS, get_style_path
from ..widgets.dialog_create_task import DialogCreateTask
from ..api.api_task import ApiTask
from ..style_util import load_styles_with_constants
from ..references_manager import references_manager


class WindowTask(QWidget):
    """Виджет содержимого задач"""
    def __init__(self):
        super().__init__()
        self.api_task = ApiTask()
        self.current_tasks_data = None  # Кэш задач
        self.selected_row = None  # Индекс выбранной строки
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
        self.ui.setStyleSheet(load_styles_with_constants(get_style_path("MAIN")))
        # Настройка контекстного меню для таблицы задач
        self.ui.tableWidget_tasks.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.tableWidget_tasks.customContextMenuRequested.connect(self._show_context_menu)
        # Подключение сигналов
        self.ui.pushButton_task_add.clicked.connect(self.on_add_clicked)
        self.ui.pushButton_task_edit.clicked.connect(self.on_edit_clicked)
        self.ui.pushButton_task_delete.clicked.connect(self.on_delete_clicked)
        self.ui.tableWidget_tasks.itemSelectionChanged.connect(self.on_selection_changed)
        self.ui.lineEdit_search.textChanged.connect(lambda text: self._filter_table(self.ui.tableWidget_tasks, text.lower()))
        # Настройка таблицы задач
        table = self.ui.tableWidget_tasks
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setSelectionMode(QAbstractItemView.SingleSelection)
        table.setFocusPolicy(Qt.NoFocus)
        for col, width in enumerate([180, 120, 120, 80, 100, 120]):
            table.setColumnWidth(col, width)
        # Настройка таблицы компонентов
        comp_table = self.ui.tableWidget_components
        for col, width in enumerate([30, 180, 60]):
            comp_table.setColumnWidth(col, width)
        # Таймер автообновления
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.load_data_from_server)

    # =============================================================================
    # УПРАВЛЕНИЕ ДАННЫМИ: ЗАГРУЗКА И ОБНОВЛЕНИЕ
    # =============================================================================
    def refresh_data(self):
        """Принудительное обновление данных"""
        self.current_tasks_data = []
        self.load_data_from_server()

    def load_data_from_server(self):
        """Загрузка задач с сервера"""
        try:
            tasks = self.api_task.get_task()
            self.update_tasks_table(tasks)
        except Exception as e:
            QMessageBox.warning(self, "Предупреждение", f"Ошибка загрузки: {e}")

    # =============================================================================
    # ОТОБРАЖЕНИЕ ДАННЫХ: ТАБЛИЦЫ И ИНФОРМАЦИОННЫЕ ПАНЕЛИ
    # =============================================================================
    def update_tasks_table(self, tasks):
        """Обновление таблицы задач с проверкой изменений"""
        if self._should_skip_update(self.current_tasks_data, tasks):
            return
        self.current_tasks_data = tasks
        self._update_table_with_selection(
            table=self.ui.tableWidget_tasks,
            data=tasks,
            columns=[
                lambda t: self.get_task_display_name(t),
                lambda t: self.get_status_name(t.get('task_status_id')),
                lambda t: self.get_department_name(t.get('department_id')),
                lambda t: str(t.get('position', '-')),
                lambda t: self._format_date(t.get('deadline_on')),
                lambda t: self._format_date(t.get('created_at'), full=True)
            ]
        )

    def _should_skip_update(self, current_data, new_data):
        """Проверка, нужно ли обновлять таблицу"""
        is_empty = self.ui.tableWidget_tasks.rowCount() == 0
        return current_data is not None and new_data == current_data and not is_empty

    def _update_table_with_selection(self, table, data, columns):
        """Обновляет таблицу и восстанавливает выделение"""
        prev_selection = self.selected_row
        table.setRowCount(0)
        table.setRowCount(len(data))
        for row, item in enumerate(data):
            for col_idx, getter in enumerate(columns):
                cell = QTableWidgetItem(getter(item))
                cell.setFlags(cell.flags() & ~Qt.ItemIsEditable)
                table.setItem(row, col_idx, cell)
        if prev_selection is not None and prev_selection < len(data):
            table.selectRow(prev_selection)

    def _format_date(self, date_str, full=False):
        """Форматирует ISO-дату в читаемый вид"""
        if not date_str:
            return "-"
        try:
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            fmt = '%d.%m.%Y %H:%M' if full else '%d.%m.%Y'
            return dt.strftime(fmt)
        except:
            return "-"

    def get_task_display_name(self, task):
        """Возвращает название задачи: артикул профиля или имя изделия"""
        if task.get('profile_tool_id'):
            tool_data = references_manager.get_profile_tool().get(task['profile_tool_id'])
            if tool_data and tool_data.get('profile_id'):
                profile = references_manager.get_profile().get(tool_data['profile_id'])
                return profile.get('article', f"Профиль {task['profile_tool_id']}")
            return f"Профиль {task['profile_tool_id']}"
        product = references_manager.get_product().get(task.get('product_id'))
        return product.get('name', f"Изделие {task.get('product_id', 'N/A')}")

    def get_status_name(self, status_id):
        """Получение названия статуса по ID"""
        return references_manager.get_task_status().get(status_id, {}).get('name', '-')

    def get_department_name(self, department_id):
        """Получение названия отдела по ID"""
        return references_manager.get_department().get(department_id, '-')

    def update_task_info_panel(self, task):
        """Обновление панели информации о задаче"""
        name = self.get_task_display_name(task)
        status = self.get_status_name(task.get('task_status_id'))
        dept = self.get_department_name(task.get('department_id'))
        deadline = self._format_date(task.get('deadline_on'))
        created = self._format_date(task.get('created_at'), full=True)
        self.ui.label_task_name.setText(f"Название: {name}")
        self.ui.label_task_department.setText(f"Отдел: {dept} | Статус: {status} | Срок: {deadline} | Создано: {created}")

    def clear_task_info_panel(self):
        """Очистка панели задачи"""
        self.ui.label_task_name.setText("Название: -")
        self.ui.label_task_department.setText("Отдел: - | Статус: - | Срок: - | Создано: -")

    def load_task_components(self, task_id):
        """Загрузка компонентов задачи"""
        try:
            components = [c for c in self.api_task.get_task_component(task_id) if c.get('task_id') == task_id]
            self.update_components_table(components)
        except:
            self.clear_components_table()

    def update_components_table(self, components):
        """Обновление таблицы компонентов"""
        self.ui.tableWidget_components.setRowCount(len(components))
        for row, comp in enumerate(components):
            num_item = QTableWidgetItem(str(row + 1))
            num_item.setFlags(num_item.flags() & ~Qt.ItemIsEditable)
            self.ui.tableWidget_components.setItem(row, 0, num_item)
            name_item = QTableWidgetItem(comp.get('name', ''))
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
            self.ui.tableWidget_components.setItem(row, 1, name_item)
            qty_item = QTableWidgetItem(str(comp.get('quantity', 0)))
            qty_item.setFlags(qty_item.flags() & ~Qt.ItemIsEditable)
            self.ui.tableWidget_components.setItem(row, 2, qty_item)

    def clear_components_table(self):
        """Очистка таблицы компонентов"""
        self.ui.tableWidget_components.setRowCount(0)

    # =============================================================================
    # ОБРАБОТЧИКИ СОБЫТИЙ: УПРАВЛЕНИЕ ЗАДАЧАМИ
    # =============================================================================
    def on_add_clicked(self):
        """Открытие диалога создания задачи"""
        self._open_dialog(DialogCreateTask, 'task_created', self.on_task_created)

    def on_task_created(self, task_data):
        """Обработка успешного создания задачи"""
        try:
            array_component_data = task_data.pop("array_component_data", [])
            response = self.api_task.create_task(task_data)
            if not response or 'id' not in response:
                QMessageBox.critical(self, "Ошибка", f"Неожиданный ответ сервера: {response}")
                return
            task_id = response['id']
            # Создание компонентов
            for comp_data in array_component_data:
                comp_request = self._build_component_request(comp_data, task_id)
                if comp_request:
                    comp_response = self.api_task.create_task_component(comp_request)
                    if not (comp_response and 'id' in comp_response):
                        print(f"Предупреждение: не удалось добавить компонент: {comp_request}")
            # Обновление интерфейса
            self.refresh_data()
            QMessageBox.information(self, "Успех", "Задача создана успешно!")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось создать задачу: {e}")

    def _build_component_request(self, comp_data, task_id):
        """Формирует запрос на создание компонента задачи"""
        if "profile_tool_component_id" in comp_data:
            return {
                "task_id": task_id,
                "profile_tool_component_id": comp_data["profile_tool_component_id"],
                "quantity": comp_data.get("quantity", 1)
            }
        elif "product_component_id" in comp_data:
            return {
                "task_id": task_id,
                "product_component_id": comp_data["product_component_id"],
                "quantity": comp_data.get("quantity", 1)
            }
        return None

    def _open_dialog(self, dialog_class, signal_name, callback):
        """Унифицированное открытие диалога"""
        try:
            dialog = dialog_class(self)
            getattr(dialog, signal_name).connect(callback)
            dialog.exec()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось открыть диалог: {e}")

    def on_edit_clicked(self):
        """Редактирование задачи"""
        if not self._get_selected_row():
            QMessageBox.warning(self, "Редактирование", "Выберите задачу для редактирования.")
        else:
            QMessageBox.information(self, "Редактировать", "Функция будет реализована позже")

    def on_delete_clicked(self):
        """Удаление задачи с подтверждением"""
        row = self._get_selected_row()
        if row is None:
            QMessageBox.warning(self, "Удаление", "Выберите задачу для удаления.")
            return
        task = self.current_tasks_data[row]
        task_name = self.get_task_display_name(task)
        if not self._confirm_deletion(f"Задачу\nНазвание: {task_name}"):
            return
        try:
            self.api_task.delete_task(task['id'])
            QMessageBox.information(self, "Удаление", "Задача успешно удалена.")
            self.refresh_data()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось удалить задачу: {e}")

    def _get_selected_row(self):
        """Возвращает индекс выбранной строки или None"""
        selected = self.ui.tableWidget_tasks.selectedItems()
        return selected[0].row() if selected else None

    def _confirm_deletion(self, item_name):
        """Запрос подтверждения удаления"""
        reply = QMessageBox.question(
            self, "Удалить",
            f"Вы действительно хотите удалить {item_name}?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        return reply == QMessageBox.Yes

    def _show_context_menu(self, pos):
        """Показать контекстное меню для изменения статуса задачи"""
        table = self.ui.tableWidget_tasks
        index = table.indexAt(pos)
        if not index.isValid():
            return

        row = index.row()
        task = self.current_tasks_data[row]
        status_dict = references_manager.get_task_status()

        menu = QMenu(table)
        menu.addSeparator()
        status_menu = QMenu("Изменить статус", menu)

        current_status_id = task.get('task_status_id')
        for status_id, status_name in status_dict.items():
            action = QAction(status_name, status_menu)
            action.setCheckable(True)
            action.setChecked(status_id == current_status_id)
            action.triggered.connect(lambda checked, sid=status_id, r=row: self._change_task_status(r, sid))
            status_menu.addAction(action)

        menu.addMenu(status_menu)
        menu.exec(table.viewport().mapToGlobal(pos))

    def _change_task_status(self, row, status_id):
        """Изменить статус задачи через API"""
        task = self.current_tasks_data[row]
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
        row = self._get_selected_row()
        if row is not None:
            self.selected_row = row
            task = self.current_tasks_data[row]
            self.update_task_info_panel(task)
            self.load_task_components(task['id'])
        else:
            self.selected_row = None
            self.clear_task_info_panel()
            self.clear_components_table()

    def _filter_table(self, table, text):
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