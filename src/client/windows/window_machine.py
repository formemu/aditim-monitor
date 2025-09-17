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
        # Таймер автообновления
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.refresh_data)

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
        machines = api_manager.machine
        work_types = api_manager.work_type
        if not machines or not work_types:
            print("Нет данных о станках или типах работ")
            self.ui.treeView_machine.setModel(model)
            return

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

            # Добавляем в нужную группу
            if work_type_id in work_type_items:
                parent_item = work_type_items[work_type_id]
                parent_item.appendRow(machine_item)
            else:
                # На всякий случай — если work_type не найден
                unknown_item = QStandardItem("Без категории")
                unknown_item.appendRow(machine_item)
                model.appendRow(unknown_item)

        # Устанавливаем модель в treeView
        self.ui.treeView_machine.setModel(model)

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
