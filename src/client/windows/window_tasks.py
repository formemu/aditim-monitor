"""
Содержимое задач для ADITIM Monitor Client
"""

from PySide6.QtWidgets import QWidget, QMessageBox, QTableWidgetItem, QAbstractItemView
from PySide6.QtCore import QFile, Qt, QTimer
from PySide6.QtUiTools import QUiLoader
from datetime import datetime

from ..constants import UI_PATHS_ABS as UI_PATHS, get_style_path
from ..widgets.dialog_create_task import DialogCreateTask
from ..api_client import ApiClient
from ..style_utils import load_styles_with_constants
from ..references_manager import references_manager
from ..async_utils import run_async


class TasksContent(QWidget):
    """Виджет содержимого задач"""
    
    def __init__(self, api_client: ApiClient = None):
        super().__init__()
        self.api_client = api_client or ApiClient()
        self.current_tasks_data = None  # Кэш данных задач (None для первой загрузки)
        self.selected_row = None  # Запоминаем выбранную строку
        self.load_ui()
        self.setup_ui()

    def load_ui(self):
        """Загрузка UI из файла"""
        ui_file = QFile(UI_PATHS["TASKS_CONTENT"])
        ui_file.open(QFile.ReadOnly)
        
        loader = QUiLoader()
        self.ui = loader.load(ui_file)
        ui_file.close()

    def setup_ui(self):
        """Настройка UI компонентов после загрузки"""
        # Применяем стили к виджету
        style_path = get_style_path("MAIN")
        style_sheet = load_styles_with_constants(style_path)
        self.ui.setStyleSheet(style_sheet)
        
        # Подключаем обработчики событий
        self.ui.pushButton_task_add.clicked.connect(self.on_add_clicked)
        self.ui.pushButton_task_edit.clicked.connect(self.on_edit_clicked)
        self.ui.pushButton_task_delete.clicked.connect(self.on_delete_clicked)
        self.ui.tableWidget_tasks.itemSelectionChanged.connect(self.on_selection_changed)
        self.ui.lineEdit_search.textChanged.connect(self.on_search_changed)
        
        # Настройка режима выделения таблицы задач
        self.ui.tableWidget_tasks.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ui.tableWidget_tasks.setSelectionMode(QAbstractItemView.SingleSelection)
        self.ui.tableWidget_tasks.setFocusPolicy(Qt.NoFocus)
        
        # Настройка ширины колонок основной таблицы
        self.ui.tableWidget_tasks.setColumnWidth(0, 180)  # Название
        self.ui.tableWidget_tasks.setColumnWidth(1, 120)  # Статус
        self.ui.tableWidget_tasks.setColumnWidth(2, 120)  # Отдел
        self.ui.tableWidget_tasks.setColumnWidth(3, 80)   # Позиция
        self.ui.tableWidget_tasks.setColumnWidth(4, 100)  # Срок
        self.ui.tableWidget_tasks.setColumnWidth(5, 120)  # Создано
        
        # Настройка таблицы компонентов
        self.ui.tableWidget_components.setColumnWidth(0, 30)   # №
        self.ui.tableWidget_components.setColumnWidth(1, 180)  # Название
        self.ui.tableWidget_components.setColumnWidth(2, 60)   # Количество
        
        # Настройка автоматического обновления
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.load_tasks_async)

    def on_add_clicked(self):
        """Добавление новой задачи"""
        try:
            # Создаем диалог создания задачи
            dialog = DialogCreateTask(self)
            
            # Подключаем сигнал успешного создания задачи
            dialog.task_created.connect(self.on_task_created)
            
            # Показываем модальный диалог
            result = dialog.exec()
            
        except Exception as e:
            print(f"TasksContent: ОШИБКА при создании диалога: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Ошибка", f"Не удалось открыть диалог создания задачи: {e}")

    def on_task_created(self, task_data):
        """Обработчик успешного создания задачи"""
        try:
            print(f"TasksContent: Получены данные для создания задачи: {task_data}")
            
            # Извлекаем компоненты отдельно
            array_component_id = task_data.pop("array_component_id", [])
            
            # Создаем задачу на сервере (без компонентов)
            response = self.api_client.create_task(task_data)
            print(f"TasksContent: Ответ сервера при создании задачи: {response}")
            
            # FastAPI возвращает объект напрямую, не в обертке success/data
            if response and 'id' in response:
                created_task = response
                task_id = created_task.get('id')
                print(f"TasksContent: Задача создана успешно с ID: {task_id}")
                
                # Если есть компоненты, создаем их для задачи
                if array_component_id:
                    for component_id in array_component_id:
                        component_data = {
                            "task_id": task_id,
                            "profile_tool_component_id": component_id
                        }
                        print(f"TasksContent: Создаем компонент {component_id} для задачи {task_id}")
                        comp_response = self.api_client.create_task_component(component_data)
                        print(f"TasksContent: Ответ при создании компонента: {comp_response}")
                        
                        if comp_response and 'id' in comp_response:
                            print(f"Компонент {component_id} добавлен к задаче {task_id}")
                        else:
                            print(f"Предупреждение: не удалось добавить компонент {component_id}: {comp_response}")
                
                # Принудительно перезагружаем список задач с сервера
                self.current_tasks_data = []  # Сбрасываем кэш для принудительного обновления
                self.load_tasks_from_server()
                
                QMessageBox.information(self, "Успех", "Задача создана успешно!")
            else:
                print(f"TasksContent: Неожиданный формат ответа: {response}")
                QMessageBox.critical(self, "Ошибка", f"Неожиданный ответ от сервера: {response}")
                    
        except Exception as e:
            print(f"TasksContent: ОШИБКА при создании задачи: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Ошибка", f"Не удалось создать задачу: {e}")

    def on_edit_clicked(self):
        """Редактирование задачи"""
        selected_items = self.ui.tableWidget_tasks.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Редактирование", "Сначала выберите задачу для редактирования.")
            return
        QMessageBox.information(self, "Редактировать", "Функция редактирования задачи будет реализована позже")

    def on_delete_clicked(self):
        """Удаление задачи с подтверждением"""
        selected_items = self.ui.tableWidget_tasks.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Удаление задачи", "Сначала выберите задачу для удаления.")
            return

        row = selected_items[0].row()
        task = None
        if self.current_tasks_data and row < len(self.current_tasks_data):
            task = self.current_tasks_data[row]
        if not task:
            QMessageBox.warning(self, "Удаление задачи", "Не удалось получить данные задачи.")
            return

        task_name = self.get_task_display_name(task)

        # Подтверждение удаления задачи
        reply = QMessageBox.question(
            self,
            "Удалить задачу",
            f"Вы действительно хотите удалить задачу?\nНазвание: {task_name}",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return

        try:
            self.api_client.delete_task(task['id'])
            QMessageBox.information(self, "Удаление", "Задача успешно удалена.")
            self.refresh_data()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось удалить задачу: {e}")

    def on_selection_changed(self):
        """Изменение выбранной задачи"""
        selected_items = self.ui.tableWidget_tasks.selectedItems()
        if selected_items:
            row = selected_items[0].row()
            self.selected_row = row
            
            # Получаем данные задачи
            task = None
            if self.current_tasks_data and row < len(self.current_tasks_data):
                task = self.current_tasks_data[row]
            
            if task:
                self.update_task_info_panel(task)
                self.load_task_components(task['id'])
            else:
                self.clear_task_info_panel()
                self.clear_components_table()
        else:
            self.selected_row = None
            self.clear_task_info_panel()
            self.clear_components_table()

    def update_task_info_panel(self, task):
        """Обновляет панель информации о задаче"""
        task_name = self.get_task_display_name(task)
        status_name = self.get_status_name(task.get('task_status_id'))
        department_name = self.get_department_name(task.get('department_id'))
        
        # Форматируем даты
        deadline = task.get('deadline_on', '')
        if deadline:
            try:
                deadline_dt = datetime.fromisoformat(deadline.replace('Z', '+00:00'))
                deadline = deadline_dt.strftime('%d.%m.%Y')
            except:
                pass
        
        created = task.get('created_at', '')
        if created:
            try:
                created_dt = datetime.fromisoformat(created.replace('Z', '+00:00'))
                created = created_dt.strftime('%d.%m.%Y %H:%M')
            except:
                pass
        
        # Используем только существующие элементы
        self.ui.label_task_name.setText(f"Название: {task_name}")
        self.ui.label_task_department.setText(f"Отдел: {department_name} | Статус: {status_name} | Срок: {deadline or '-'} | Создано: {created or '-'}")

    def clear_task_info_panel(self):
        """Очищает панель информации о задаче"""
        self.ui.label_task_name.setText("Название: -")
        self.ui.label_task_department.setText("Отдел: - | Статус: - | Срок: - | Создано: -")

    def get_task_display_name(self, task):
        """Получает отображаемое название задачи используя кэшированные данные"""
        # Логика: если profile_tool_id != NULL → артикул профиля, иначе название изделия
        if task.get('profile_tool_id'):
            # Получаем артикул профиля через кэшированные данные
            tool_data = references_manager.get_profile_tool(task['profile_tool_id'])
            if tool_data and tool_data.get('profile_id'):
                profile_data = references_manager.get_profile(tool_data['profile_id'])
                if profile_data:
                    return profile_data.get('article', f"Профиль {task['profile_tool_id']}")
            return f"Профиль {task['profile_tool_id']}"
        else:
            # Получаем название изделия из кэша
            product_data = references_manager.get_product(task.get('product_id'))
            if product_data:
                return product_data.get('name', f"Изделие {task.get('product_id', 'N/A')}")
            return f"Изделие {task.get('product_id', 'N/A')}"

    def get_status_name(self, status_id):
        """Получает название статуса по ID"""
        try:
            status_data = references_manager.get_task_status(status_id)
            return status_data.get('name', '-') if status_data else '-'
        except:
            return '-'

    def get_department_name(self, department_id):
        """Получает название отдела по ID"""
        try:
            departments = references_manager.get_departments()
            return departments.get(department_id, '-')
        except:
            return '-'

    def load_task_components(self, task_id):
        """Загружает компоненты задачи"""
        try:
            components = self.api_client.get_task_component(task_id=task_id)
            task_components = [c for c in components if c.get('task_id') == task_id]
            self.update_components_table(task_components)
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.clear_components_table()

    def update_components_table(self, components):
        """Обновляет таблицу компонентов"""
        self.ui.tableWidget_components.setRowCount(len(components))
        
        for row, component in enumerate(components):
            # № п/п
            num_item = QTableWidgetItem(str(row + 1))
            num_item.setFlags(num_item.flags() & ~Qt.ItemIsEditable)
            self.ui.tableWidget_components.setItem(row, 0, num_item)
            
            # Название компонента
            name_item = QTableWidgetItem(component.get('name', ''))
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
            self.ui.tableWidget_components.setItem(row, 1, name_item)
            
            # Количество
            quantity_item = QTableWidgetItem(str(component.get('quantity', 0)))
            quantity_item.setFlags(quantity_item.flags() & ~Qt.ItemIsEditable)
            self.ui.tableWidget_components.setItem(row, 2, quantity_item)

    def clear_components_table(self):
        """Очищает таблицу компонентов"""
        self.ui.tableWidget_components.setRowCount(0)

    def on_search_changed(self, text):
        """Поиск по названию задачи"""
        for row in range(self.ui.tableWidget_tasks.rowCount()):
            item = self.ui.tableWidget_tasks.item(row, 0)  # Колонка "Название"
            if item:
                visible = text.lower() in item.text().lower()
                self.ui.tableWidget_tasks.setRowHidden(row, not visible)

    def refresh_data(self):
        """Публичный метод для принудительного обновления данных"""
        self.current_tasks_data = []  # Сбрасываем кэш
        self.load_tasks_from_server()

    def load_tasks_from_server(self):
        """Загружает задачи с сервера асинхронно"""
        try:
            # Показываем индикатор загрузки (можно добавить spinner)
            self.ui.tableWidget_tasks.setEnabled(False)
            
            # Запускаем асинхронную загрузку
            run_async(
                self.api_client.get_task,
                on_success=self._on_tasks_loaded,
                on_error=self._on_tasks_load_error
            )
        except Exception as e:
            self._on_tasks_load_error(e)

    def _on_tasks_loaded(self, tasks):
        """Обработчик успешной загрузки задач"""
        try:
            self.ui.tableWidget_tasks.setEnabled(True)
            self.update_tasks_table(tasks)
        except Exception as e:
            self._on_tasks_load_error(e)

    def _on_tasks_load_error(self, error):
        """Обработчик ошибки загрузки задач"""
        self.ui.tableWidget_tasks.setEnabled(True)
        QMessageBox.warning(self, "Предупреждение", f"Не удалось загрузить задачи с сервера: {error}")

    def load_tasks_async(self):
        """Асинхронная загрузка задач для таймера"""
        if self.ui.tableWidget_tasks.isEnabled():  # Не загружаем если уже идет загрузка
            self.load_tasks_from_server()

    def update_tasks_table(self, tasks):
        """Обновляет таблицу задач с проверкой изменений"""
        # Проверяем если таблица пустая - обновляем принудительно
        is_table_empty = self.ui.tableWidget_tasks.rowCount() == 0
        
        # Сравниваем новые данные с кэшем
        if self.current_tasks_data is not None and tasks == self.current_tasks_data and not is_table_empty:
            return  # Данные не изменились и таблица не пустая, не обновляем
        
        # Сохраняем текущее выделение
        current_selection = None
        selected_items = self.ui.tableWidget_tasks.selectedItems()
        if selected_items:
            current_selection = selected_items[0].row()
        
        # Обновляем кэш
        self.current_tasks_data = tasks
        
        # Очищаем таблицу
        self.ui.tableWidget_tasks.setRowCount(0)
        
        # Заполняем таблицу данными с сервера
        self.ui.tableWidget_tasks.setRowCount(len(tasks))
        
        for row, task in enumerate(tasks):
            # Название (логика: профиль или изделие)
            name_item = QTableWidgetItem(self.get_task_display_name(task))
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
            self.ui.tableWidget_tasks.setItem(row, 0, name_item)
            
            # Статус
            status_item = QTableWidgetItem(self.get_status_name(task.get('task_status_id')))
            status_item.setFlags(status_item.flags() & ~Qt.ItemIsEditable)
            self.ui.tableWidget_tasks.setItem(row, 1, status_item)
            
            # Отдел
            department_item = QTableWidgetItem(self.get_department_name(task.get('department_id')))
            department_item.setFlags(department_item.flags() & ~Qt.ItemIsEditable)
            self.ui.tableWidget_tasks.setItem(row, 2, department_item)
            
            # Позиция
            position_item = QTableWidgetItem(str(task.get('position', '-')))
            position_item.setFlags(position_item.flags() & ~Qt.ItemIsEditable)
            self.ui.tableWidget_tasks.setItem(row, 3, position_item)
            
            # Срок
            deadline = task.get('deadline_on', '')
            if deadline:
                try:
                    deadline_dt = datetime.fromisoformat(deadline.replace('Z', '+00:00'))
                    deadline = deadline_dt.strftime('%d.%m.%Y')
                except:
                    pass
            deadline_item = QTableWidgetItem(deadline or '-')
            deadline_item.setFlags(deadline_item.flags() & ~Qt.ItemIsEditable)
            self.ui.tableWidget_tasks.setItem(row, 4, deadline_item)
            
            # Создано
            created = task.get('created_at', '')
            if created:
                try:
                    created_dt = datetime.fromisoformat(created.replace('Z', '+00:00'))
                    created = created_dt.strftime('%d.%m.%Y')
                except:
                    pass
            created_item = QTableWidgetItem(created or '-')
            created_item.setFlags(created_item.flags() & ~Qt.ItemIsEditable)
            self.ui.tableWidget_tasks.setItem(row, 5, created_item)
        
        # Восстанавливаем выделение если возможно
        if current_selection is not None and current_selection < len(tasks):
            self.ui.tableWidget_tasks.selectRow(current_selection)
            self.selected_row = current_selection

    def start_auto_refresh(self):
        """Запускает автоматическое обновление данных"""
        if not self.update_timer.isActive():
            self.update_timer.start(5000)  # 5 секунд
            # Сразу загружаем данные при активации
            self.load_tasks_async()

    def stop_auto_refresh(self):
        """Останавливает автоматическое обновление данных"""
        if self.update_timer.isActive():
            self.update_timer.stop()
