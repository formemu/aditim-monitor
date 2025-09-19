"""
Станки ADITIM Monitor Client
"""
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, QTimer, Qt

from ..constant import UI_PATHS_ABS
from ..api_manager import api_manager

class WindowMachine(QWidget):
    """Виджет станков"""

    def __init__(self):
        super().__init__()
        self.load_ui()
        self.setup_ui()
        self.setup_tree()

    # =============================================================================
    # ИНИЦИАЛИЗАЦИЯ И ЗАГРУЗКА ИНТЕРФЕЙСА
    # =============================================================================

    def load_ui(self):
        """Загрузка UI из файла"""
        ui_file = QFile(UI_PATHS_ABS["MACHINE_CONTENT"])
        ui_file.open(QFile.ReadOnly)
        loader = QUiLoader()
        self.ui = loader.load(ui_file)
        ui_file.close()
    
    
    def setup_ui(self):
        """Настройка UI компонентов"""

        self.refresh_data()
        self.ui.treeView_machine.clicked.connect(self.on_machine_clicked)

    # =============================================================================
    # УПРАВЛЕНИЕ ДАННЫМИ: ЗАГРУЗКА И ОБНОВЛЕНИЕ
    # =============================================================================
    def refresh_data(self):
        """Принудительное обновление данных"""
        pass

    def setup_tree(self):
        """Настройка дерева станков: группировка по типам работ (work_type)"""
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(["Станки"])

        # Получаем данные из api_manager
        machines = api_manager.directory['machine']
        work_types = api_manager.directory['work_type']

        # Создаём словарь work_type_id → QStandardItem
        work_type_items = {}
        for wt in work_types:
            item = QStandardItem(wt["name"])
            item.setSelectable(False)  # Группу нельзя выбирать как станок
            work_type_items[wt["id"]] = item
            model.appendRow(item)

        # Добавляем станки в соответствующие группы
        for machine in machines:
            machine_name = machine["name"]
            work_type_id = machine["work_type_id"]
            machine_item = QStandardItem(machine_name)
            machine_item.setData(machine, role=Qt.UserRole)  # Сохраняем весь объект

            if work_type_id in work_type_items:
                parent_item = work_type_items[work_type_id]
                parent_item.appendRow(machine_item)


        # Устанавливаем модель в treeView
        self.ui.treeView_machine.setModel(model)

    def on_machine_clicked(self, index):
        """Обработка клика по станку — показываем задачи для этого станка"""
        item = self.ui.treeView_machine.model().itemFromIndex(index)
        machine = item.data(Qt.UserRole)

        # Проверяем, что это лист (сам станок), а не группа
        if not machine or "work_type_id" not in machine:
            # Это группа (work_type), не станок
            self.ui.listView_machine_task.setModel(None)
            return

        
        print(api_manager.directory['machine'])

        # Находим все этапы (task_component_stage), привязанные к этому станку
        stages_for_machine = [
            stage for stage in api_manager.directory['machine']
            if stage["machine_id"] == machine["id"]
        ]
        print(stages_for_machine)
        # Теперь получим все task_component, к которым относятся эти этапы
        task_component_ids = {stage["task_component_id"] for stage in stages_for_machine if stage.get("task_component_id")}

        # Найдём сами задачи через task_component → task
        task_ids = set()
        tasks = []
        for tc_id in task_component_ids:
            # Найдём task_component по id
            task_component = next(
                (tc for tc in api_manager.task_component if tc["id"] == tc_id),
                None
            )
            if task_component and task_component["task_id"] not in task_ids:
                task = api_manager.get_task_by_id(task_component["task_id"])
                if task:
                    tasks.append(task)
                    task_ids.add(task["task_id"])

        # Сортируем по позиции или дедлайну
        tasks.sort(key=lambda x: (x.get("position") or 0))

        # Создаём модель для listView
        list_model = QStandardItemModel()
        for task in tasks:
            task_name = f"Задача #{task['id']} — {task.get('product_name', 'Без названия')}"
            item = QStandardItem(task_name)
            item.setData(task, Qt.UserRole)
            list_model.appendRow(item)

        self.ui.listView_machine_task.setModel(list_model)

    

