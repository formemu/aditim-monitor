"""Содержимое изделий для ADITIM Monitor Client с вкладками и компонентами"""
from PySide6.QtWidgets import QWidget, QMessageBox, QTableWidgetItem, QAbstractItemView, QHeaderView, QTableWidgetItem, QTableWidget
from PySide6.QtCore import QFile, Qt
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QColor
from ..constant import UI_PATHS_ABS, get_style_path
from ..style_util import load_styles
from ..api_manager import api_manager
from ..widgets.profile_tool.dialog_create_profile_tool import DialogCreateProfileTool
from ..widgets.profile_tool.dialog_edit_profile_tool import DialogEditProfileTool
from ..widgets.product.dialog_create_product import DialogCreateProduct
from ..widgets.product.dialog_edit_product import DialogEditProduct

class WindowProduct(QWidget):
    """Виджет содержимого изделий с вкладками"""
    
    def __init__(self):
        super().__init__()
        self.tab_index = 0 
        self.selected_row = 0 
        self.profile_tool = None
        self.product = None
        self.load_ui()
        self.setup_ui()
        self.connect_signals()

    # =============================================================================
    # ИНИЦИАЛИЗАЦИЯ И ЗАГРУЗКА ИНТЕРФЕЙСА
    # =============================================================================
    def load_ui(self):
        """Загрузка UI из файла"""
        ui_file = QFile(UI_PATHS_ABS["PRODUCT_CONTENT"])
        ui_file.open(QFile.ReadOnly)
        loader = QUiLoader()
        self.ui = loader.load(ui_file)
        ui_file.close()

    def setup_ui(self):
        """Настройка UI компонентов"""
        self.ui.setStyleSheet(load_styles(get_style_path("MAIN")))
        # Общие подключения
        self.ui.pushButton_component_add.clicked.connect(self.on_component_add_clicked)
        self.ui.pushButton_component_edit.clicked.connect(self.on_component_edit_clicked)
        self.ui.pushButton_component_delete.clicked.connect(self.on_component_delete_clicked)
        self.ui.tabWidget_products.currentChanged.connect(self.on_tab_changed)
        # Подключения: профили
        self.ui.pushButton_profile_tool_add.clicked.connect(self.on_profile_tool_add_clicked)
        self.ui.pushButton_profile_tool_edit.clicked.connect(self.on_profile_tool_edit_clicked)
        self.ui.pushButton_profile_tool_delete.clicked.connect(self.on_profile_tool_delete_clicked)
        self.ui.tableWidget_profile_tool.itemSelectionChanged.connect(self.on_selection_changed)
        self.ui.lineEdit_search_profile_tool.textChanged.connect(self.filter_table)
        # Подключения: изделия
        self.ui.pushButton_product_add.clicked.connect(self.on_product_add_clicked)
        self.ui.pushButton_product_edit.clicked.connect(self.on_product_edit_clicked)
        self.ui.pushButton_product_delete.clicked.connect(self.on_product_delete_clicked)
        self.ui.tableWidget_product.itemSelectionChanged.connect(self.on_selection_changed)
        self.ui.lineEdit_search_product.textChanged.connect(self.filter_table)

        #подключение сигналов таблицы компонетов
        self.ui.tableWidget_component.itemSelectionChanged.connect(self.on_selection_component_changed)
        # Настройка таблиц
        for table in [self.ui.tableWidget_profile_tool, self.ui.tableWidget_product, self.ui.tableWidget_component]:
            table.setSelectionBehavior(QAbstractItemView.SelectRows)
            table.setSelectionMode(QAbstractItemView.SingleSelection)
            table.setFocusPolicy(Qt.NoFocus)
        self.ui.tableWidget_profile_tool.setColumnWidth(0, 200)
        self.ui.tableWidget_profile_tool.horizontalHeader().setStretchLastSection(True)
        self.ui.tableWidget_product.setColumnWidth(0, 200)
        self.ui.tableWidget_product.setColumnWidth(1, 150)
        self.ui.tableWidget_product.horizontalHeader().setStretchLastSection(True)
        self.ui.tableWidget_component.setColumnWidth(0, 300)
        self.ui.tableWidget_component.horizontalHeader().setStretchLastSection(True)

        self.ui.tableWidget_component_stage.setColumnCount(7)
        self.ui.tableWidget_component_stage.setHorizontalHeaderLabels([
            "№", "Операция", "Станок", "Начало", "Окончание", "Описание", "ID"
        ])
        # self.ui.tableWidget_component_stage.setColumnHidden(6, True)
        # self.ui.tableWidget_component_stage.setSortingEnabled(True)
        # self.ui.tableWidget_component_stage.setEditTriggers(QTableWidget.NoEditTriggers)
        # self.ui.tableWidget_component_stage.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)

        # Инициализация таблицы
        self.refresh_data()

    # =============================================================================
    # УПРАВЛЕНИЕ ДАННЫМИ: ЗАГРУЗКА И ОБНОВЛЕНИЕ
    # =============================================================================
    def refresh_data(self):
        """Принудительное обновление данных"""
        if self.tab_index == 0:
            self.update_table_profile_tool()
        elif self.tab_index == 1:
            self.update_table_product()


    def connect_signals(self):
        """Подключаемся к сигналам ApiManager"""
        api_manager.data_updated.connect(self.on_data_updated)

    def on_data_updated(self, group: str, key: str, success: bool):
        """Реакция на обновление данных"""
        if success and group == "table" and key == "profile_tool":
            self.update_table_profile_tool()
            if self.profile_tool:
                self.profile_tool = api_manager.get_by_id("profile_tool", self.profile_tool['id'])
                self.load_profile_tool_component(self.profile_tool['id'])
        elif success and group == "table" and key == "product":
            self.update_table_product()
            if self.product:
                self.product = api_manager.get_by_id("product", self.product['id'])
                self.load_product_component(self.product['id'])

    def on_tab_changed(self):
        """Обработчик смены вкладки — обновляет данные для выбранной вкладки"""
        self.tab_index = self.ui.tabWidget_products.currentIndex()
        self.clear_info_panel()
        self.selected_row = 0
        self.profile_tool = None
        self.product = None
        self.ui.tableWidget_profile_tool.setCurrentItem(None)
        self.ui.tableWidget_product.setCurrentItem(None)

    # =============================================================================
    # ОТОБРАЖЕНИЕ ДАННЫХ: ТАБЛИЦЫ И ИНФОРМАЦИОННЫЕ ПАНЕЛИ
    # =============================================================================
    def update_table_profile_tool(self):
        """Обновление таблицы инструментов профиля с корректным отображением и заполнением по ширине"""
        table = self.ui.tableWidget_profile_tool
        table.setRowCount(len(api_manager.table['profile_tool']))
        table.setColumnCount(4)
        # Заголовки столбцов 
        table.setHorizontalHeaderLabels(["ID",  "Профиль", "Размер ","Описание"])
        header = table.horizontalHeader()
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.Stretch)
        for row, tool in enumerate(api_manager.table['profile_tool']):
            id = tool['id']
            table.setItem(row, 0, QTableWidgetItem(str(id)))
            name = tool['profile']['article']
            table.setItem(row, 1, QTableWidgetItem(name))
            dimension = tool['dimension']['name']
            table.setItem(row, 2, QTableWidgetItem(dimension))
            description = tool['description']
            table.setItem(row, 3, QTableWidgetItem(description))
        table.setColumnHidden(0, True)

    def update_table_product(self):
        """Обновление таблицы изделий с корректным отображением и заполнением по ширине"""
        table = self.ui.tableWidget_product
        table.setRowCount(len(api_manager.table['product']))
        table.setColumnCount(4)
        # Заголовки столбцов
        table.setHorizontalHeaderLabels(["ID", "Название", "Департамент", "Описание"])
        header = table.horizontalHeader()
        
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        for row, product in enumerate(api_manager.table['product']):
            id = product['id']
            table.setItem(row, 0, QTableWidgetItem(str(id)))
            name = product['name']
            table.setItem(row, 1, QTableWidgetItem(name))
            dept = product['department']['name']
            table.setItem(row, 2, QTableWidgetItem(dept))
            desc = product['description']
            table.setItem(row, 3, QTableWidgetItem(desc))
        table.setColumnHidden(0, True)

    def load_profile_tool_component(self, item_id):
        """Загрузка компонентов инструмента профиля"""
        list_component = self.profile_tool['component']

        self.ui.label_selected_item.setText(f"ID: {item_id}")
        self.ui.tableWidget_component.setRowCount(0)
        self.ui.tableWidget_component.setColumnCount(2)
        self.ui.tableWidget_component.setHorizontalHeaderLabels(["Название", "Статус"])
        self.ui.tableWidget_component.setRowCount(len(list_component))
        for row, component in enumerate(list_component):
            name = component["type"]["name"]
            status = component["status"]["name"]
            name_item = QTableWidgetItem(name)
            name_item.setData(Qt.UserRole, component["id"])
            status_item = QTableWidgetItem(status)
            self.ui.tableWidget_component.setItem(row, 0, name_item)
            self.ui.tableWidget_component.setItem(row, 1, status_item)

    def load_product_component(self, item_id):
        """Загрузка компонентов изделия"""
        list_component = self.product['component']
        self.ui.label_selected_item.setText(f"ID: {item_id}")
        self.ui.tableWidget_component.setRowCount(0)
        self.ui.tableWidget_component.setRowCount(len(list_component))
        for row, component in enumerate(list_component):
            name = component["name"]
            quantity = component["quantity"]
            name_item = QTableWidgetItem(name)
            name_item.setData(Qt.UserRole, component["id"])
            quantity_item = QTableWidgetItem(str(quantity))
            self.ui.tableWidget_component.setItem(row, 0, name_item)
            self.ui.tableWidget_component.setItem(row, 1, quantity_item)

    def clear_info_panel(self):
        """Очистка панели компонентов"""
        self.ui.tableWidget_component.setRowCount(0)
        self.ui.label_selected_item.setText("Выберите изделие")
        self.ui.label_component_description.setText("Описание: -")

    def filter_table(self):
        """Фильтрация строк таблицы"""
        if self.tab_index == 0:
            table = self.ui.tableWidget_profile_tool
            text = self.ui.lineEdit_search_profile_tool.text().lower()
        else:
            table = self.ui.tableWidget_product
            text = self.ui.lineEdit_search_product.text().lower()

        for row in range(table.rowCount()):
            item = table.item(row, 1)
            if item:
                visible = text.lower() in item.text().lower()
                table.setRowHidden(row, not visible)

    # =============================================================================
    # ОБРАБОТЧИКИ СОБЫТИЙ: ДАННЫЕ ТАБЛИЦЫ И ИНФОРМАЦИОННОЙ ПАНЕЛИ
    # =============================================================================
    def on_selection_changed(self):
        """Обработчик выбора элемента"""
        if self.tab_index == 0:
            self.selected_row = self.ui.tableWidget_profile_tool.currentRow()
            item = self.ui.tableWidget_profile_tool.item(self.selected_row, 0)
            if item:
                profile_tool_id = item.text()
                self.profile_tool = api_manager.get_by_id('profile_tool', profile_tool_id)
                self.load_profile_tool_component(profile_tool_id)
        elif self.tab_index == 1:
            self.selected_row = self.ui.tableWidget_product.currentRow()
            item = self.ui.tableWidget_product.item(self.selected_row, 0)
            if item:
                product_id = item.text()
                self.product = api_manager.get_by_id('product', product_id)
                self.load_product_component(product_id)

    def on_selection_component_changed(self):
        """Обработка выбора компонента"""

        self.update_table_component_stage()

    def update_table_component_stage(self):
        """
        Заполняет tableWidget_component_stage для изделия:
        группировка по задачам (type.name), внутри — этапы
        """


        # self.ui.tableWidget_component_stage.setRowCount(0)
        stages_data = []

        # 1. Собираем все задачи, где встречается любой компонент этого изделия
        for task in api_manager.table["task"]:
            if task["profile_tool_id"] != self.profile_tool["id"]:
                continue  # только задачи на это изделие
            task_type_name = task["type"]["name"]
            print(task_type_name)
            # Добавляем заголовок группы
            stages_data.append({
                "is_header": True,
                "task_type": task_type_name,
                "task_id": task["id"]
            })

            # 2. Проходим по компонентам задачи
            for component in task["component"]:
                for stage in component["stage"]:
                    stages_data.append({
                        "is_header": False,
                        "task_type": task_type_name,
                        "task_id": task["id"],
                        "component": component,
                        "stage": stage
                    })
        # 3. Заполняем таблицу
        self.ui.tableWidget_component_stage.setRowCount(len(stages_data))

        for row, data in enumerate(stages_data):
            if data["is_header"]:
                # Заголовок группы
                item = QTableWidgetItem(data["task_type"])
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)  # Только чтение
                item.setBackground(QColor("#f0f0f0"))  # Серый фон
                font = item.font()
                font.setBold(True)
                item.setFont(font)
                self.ui.tableWidget_component_stage.setItem(row, 1, item)  # В колонку "Этап / Задача"
                # Остальные колонки пустые
                for col in [0, 2, 3, 4, 5]:
                    empty_item = QTableWidgetItem("")
                    empty_item.setBackground(QColor("#f0f0f0"))
                    empty_item.setFlags(empty_item.flags() & ~Qt.ItemIsEditable)
                    self.ui.tableWidget_component_stage.setItem(row, col, empty_item)

            else:
                stage = data["stage"]
                component = data["component"]

                # Порядковый номер
                self.ui.tableWidget_component_stage.setItem(row, 0, QTableWidgetItem(str(stage.get("stage_num", ""))))

                # Название операции: компонент + операция
                comp_name = (
                    component["profile_tool_component"]["type"]["name"]
                    if component.get("profile_tool_component")
                    else (component["product_component"]["name"] if component.get("product_component") else "Без имени")
                )
                work_name = stage["work_subtype"]["name"] if stage.get("work_subtype") else "Без операции"
                op_text = f"{comp_name} / {work_name}"
                self.ui.tableWidget_component_stage.setItem(row, 1, QTableWidgetItem(op_text))

                # Станок
                machine = stage.get("machine")
                machine_name = machine["name"] if machine else "Не назначен"
                self.ui.tableWidget_component_stage.setItem(row, 2, QTableWidgetItem(machine_name))

                # Даты
                self.ui.tableWidget_component_stage.setItem(row, 3, QTableWidgetItem(stage.get("start") or ""))
                self.ui.tableWidget_component_stage.setItem(row, 4, QTableWidgetItem(stage.get("finish") or ""))

                # Описание
                self.ui.tableWidget_component_stage.setItem(row, 5, QTableWidgetItem(stage.get("description", "")))

                # Сохраняем данные в последней скрытой колонке (например, ID=6)
                item_id = QTableWidgetItem(str(stage["id"]))
                item_id.setData(Qt.UserRole, stage)
                self.ui.tableWidget_component_stage.setItem(row, 6, item_id)



    # =============================================================================
    # ОБРАБОТЧИКИ СОБЫТИЙ: УПРАВЛЕНИЕ
    # =============================================================================
    def on_profile_tool_add_clicked(self):
        """Добавление инструмента профиля"""
        dialog = DialogCreateProfileTool(self)
        dialog.exec()

    def on_product_add_clicked(self):
        """Добавление изделия"""
        dialog = DialogCreateProduct(self)
        dialog.exec()

    def on_profile_tool_edit_clicked(self):
        """Редактирование инструмента профиля"""
        dialog = DialogEditProfileTool(self.profile_tool, self)
        dialog.exec()

    def on_product_edit_clicked(self):
        """Редактирование изделия"""
        dialog = DialogEditProduct(self.product, self)
        dialog.exec()

    def on_profile_tool_delete_clicked(self):
        """Удаление инструмента"""
        if self.profile_tool:
            api_manager.api_profile_tool.delete_profile_tool(self.profile_tool['id'])
            self.profile_tool = None
        else:
            self.show_warning_dialog("Инструмент профиля не выбран")

    def on_product_delete_clicked(self):
        """Удаление изделия"""
        if self.product:
            api_manager.api_product.delete_product(self.product['id'])
            self.product = None
        else:
            self.show_warning_dialog("Изделие не выбрано")

    def on_component_add_clicked(self):
        """Добавление компонента"""
        QMessageBox.information(self, "Информация", "Функция будет реализована позже")

    def on_component_edit_clicked(self):
        """Редактирование компонента"""
        QMessageBox.information(self, "Информация", "Функция будет реализована позже")

    def on_component_delete_clicked(self):
        """Удаление компонента"""
        QMessageBox.information(self, "Информация", "Функция будет реализована позже")

    # =============================================================================
    # ОКНО ПРЕДУПРЕЖДЕНИЯ
    # =============================================================================
    def show_warning_dialog(self, message: str):
        """Показать окно предупреждения с заданным сообщением"""
        warning_box = QMessageBox(self)
        warning_box.setIcon(QMessageBox.Warning)
        warning_box.setWindowTitle("Внимание")
        warning_box.setText(message)
        warning_box.setStandardButtons(QMessageBox.Ok)
        warning_box.exec()