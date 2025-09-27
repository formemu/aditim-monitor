"""
Станки ADITIM Monitor Client
"""
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QStandardItemModel, QStandardItem, QPixmap
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, Qt

from ..constant import UI_PATHS_ABS, ICON_PATHS_ABS, get_style_path
from ..api_manager import api_manager
from ..style_util import load_styles
from PySide6.QtWidgets import QMessageBox

class WindowMachine(QWidget):
    """Виджет станков"""

    def __init__(self):
        super().__init__()
        self.load_ui()
        self.setup_ui()
        self.setup_tree()
        self.connect_signals()

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
        self.ui.setStyleSheet(load_styles(get_style_path("MAIN")))
        self.load_logo()
        self.refresh_data()
        self.ui.treeView_machine.clicked.connect(self.on_machine_clicked)

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
    def connect_signals(self):
        """Подключаемся к сигналам ApiManager"""
        api_manager.data_updated.connect(self.on_data_updated)

    def on_data_updated(self, group: str, key: str, success: bool):
        """Реакция на обновление данных"""
        if success and group == "directory" and key == "machine":
            self.setup_tree()

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

        item = self.ui.treeView_machine.model().itemFromIndex(index)
        machine = item.data(Qt.UserRole)
        if machine is None:
            return
        machine_id = machine["id"]
        list_operation = []
        for task in api_manager.table["queue"]:
            for component in task["component"]:
                for stage in component["stage"]:
                    if stage["machine"] and stage["machine"]["id"] == machine_id:
                        list_operation.append({
                            "task": task,
                            "component": component,
                            "stage": stage
                        })

        # Отображение
        
        list_model = QStandardItemModel()
        for operation in list_operation:
            name = self.get_operation_display_name(operation)
            item = QStandardItem(name)
            item.setData(operation, Qt.UserRole)
            list_model.appendRow(item)

        self.ui.listView_machine_task.setModel(list_model)

    def get_operation_display_name(self, operation):
        """Имя для строки в listView: основывается на стадии и её контексте"""
        task = operation["task"]
        component = operation["component"]
        stage = operation["stage"]

        # 1. Основное имя: профиль или продукт
        if task["profiletool_id"]: name = task["profiletool"]['profile']['article']
        elif task["product_id"]: name = task["product"]["name"]
        else: name = "Без объекта"

        # 1.1. тип задачи
        if task["type"]: type_name = task["type"]["name"]

        # 2. Имя компонента
        if component["profiletool_component_id"]: component_name = component["profiletool_component"]["type"]["name"]
        elif component["product_component_id"]: component_name = component["product_component"]["name"]
        else: component_name = "Без компонента"

        # 3. Тип работ
        work_subtype_name = stage["work_subtype"]["name"] if stage.get("work_subtype") else "Без этапа"

        return f"{name} ({component_name}) / {work_subtype_name} - {type_name}"
    

    def show_warning_dialog(self, message: str):
        """Показать окно предупреждения с заданным сообщением"""
        QMessageBox.warning(self, "Внимание", message)

