"""
Содержимое изделий для ADITIM Monitor Client с вкладками и компонентами
"""
from PySide6.QtWidgets import QWidget, QMessageBox, QTableWidgetItem, QAbstractItemView, QHeaderView
from PySide6.QtCore import QFile, Qt, QTimer
from PySide6.QtUiTools import QUiLoader
from ..constant import UI_PATHS_ABS as UI_PATHS, get_style_path
from ..style_util import load_styles
from ..api_manager import api_manager
from ..widgets.dialog_create_profile_tool import DialogCreateProfileTool
from ..widgets.dialog_edit_profile_tool import DialogEditProfileTool
from ..widgets.dialog_create_product import DialogCreateProduct
from ..widgets.dialog_edit_product import DialogEditProduct


class WindowProduct(QWidget):
    """Виджет содержимого изделий с вкладками"""
    
    def __init__(self):
        super().__init__()
        self.tab_index = 0  # Индекс текущей вкладки
        self.selected_row = 0 # Индекс выбранной строки
        self.load_ui()
        self.setup_ui()

    # =============================================================================
    # ИНИЦИАЛИЗАЦИЯ И ЗАГРУЗКА ИНТЕРФЕЙСА
    # =============================================================================
    def load_ui(self):
        """Загрузка UI из файла"""
        ui_file = QFile(UI_PATHS["PRODUCT_CONTENT"])
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
        # Таймер автообновления
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.refresh_data)

    # =============================================================================
    # УПРАВЛЕНИЕ ДАННЫМИ: ЗАГРУЗКА И ОБНОВЛЕНИЕ
    # =============================================================================
    def refresh_data(self):
        """Принудительное обновление данных"""
        if self.tab_index == 0:
            api_manager.refresh_profile_tool_async()
            self.update_table_profile_tool()
        elif self.tab_index == 1:
            api_manager.refresh_product_async()
            self.update_table_product()

    def on_tab_changed(self):
        """Обработчик смены вкладки — обновляет данные для выбранной вкладки"""
        self.tab_index = self.ui.tabWidget_products.currentIndex()
        self.clear_component()
        self.selected_row = 0
        self.refresh_data()
    
    # =============================================================================
    # ОТОБРАЖЕНИЕ ДАННЫХ: ТАБЛИЦЫ И ИНФОРМАЦИОННЫЕ ПАНЕЛИ
    # =============================================================================
    def update_table_profile_tool(self):
        """Обновление таблицы инструментов профиля с корректным отображением и заполнением по ширине"""
        table = self.ui.tableWidget_profile_tool
        table.setRowCount(len(api_manager.profile_tool))
        table.setColumnCount(2)
        # Заголовки столбцов
        table.setHorizontalHeaderLabels(["Размер и профиль", "Описание"])
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        for row, tool in enumerate(api_manager.profile_tool):
            # Размер и профиль
            name = f"{tool['profile']['article']} - {tool['dimension']['name']}"
            table.setItem(row, 0, QTableWidgetItem(name))
            # Описание
            description = tool['description']
            table.setItem(row, 1, QTableWidgetItem(description))

    def update_table_product(self):
        """Обновление таблицы изделий с корректным отображением и заполнением по ширине"""
        table = self.ui.tableWidget_product
        table.setRowCount(len(api_manager.product))
        table.setColumnCount(3)
        # Заголовки столбцов
        table.setHorizontalHeaderLabels(["Название", "Департамент", "Описание"])
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        for row, product in enumerate(api_manager.product):
            # Название изделия
            name = product['name']
            table.setItem(row, 0, QTableWidgetItem(name))
            # Департамент
            dept = product['department']['name']
            table.setItem(row, 1, QTableWidgetItem(dept))
            # Описание
            desc = product['description']
            table.setItem(row, 2, QTableWidgetItem(desc))

    def load_profile_tool_component(self, item_id):
        """Загрузка компонентов инструмента профиля"""
        list_component = api_manager.load_profile_tool_component_by_id(item_id)
        self.ui.label_selected_item.setText(f"ID: {item_id}")
        self.ui.tableWidget_component.setRowCount(0)
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
        list_component = api_manager.load_product_component_by_id(item_id)
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

    def clear_component(self):
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
            item = table.item(row, 0)
            if item:
                visible = text.lower() in item.text().lower()
                table.setRowHidden(row, not visible)

    # =============================================================================
    # ОБРАБОТЧИКИ СОБЫТИЙ: ДАННЫЕ ТАБЛИЦЫ И ИНФОРМАЦИОННОЙ ПАНЕЛИ
    # =============================================================================
    def on_selection_changed(self):
        """Обработчик выбора элемента"""
        if self.tab_index == 0:
            self.selected_row = self.ui.tableWidget_profile_tool.selectedItems()[0].row()
            self.load_profile_tool_component(api_manager.profile_tool[self.selected_row]['id'])
        else:
            self.selected_row = self.ui.tableWidget_product.selectedItems()[0].row()
            self.load_product_component(api_manager.product[self.selected_row]['id'])

    # =============================================================================
    # ОБРАБОТЧИКИ СОБЫТИЙ: УПРАВЛЕНИЕ
    # =============================================================================
    def on_profile_tool_add_clicked(self):
        """Добавление инструмента профиля"""
        dialog = DialogCreateProfileTool(self)
        if dialog.exec():
            self.refresh_data()
            self.load_profile_tool_component(api_manager.profile_tool[self.selected_row]['id'])

    def on_product_add_clicked(self):
        """Добавление изделия"""
        dialog = DialogCreateProduct(self)
        if dialog.exec():
            self.refresh_data()
            self.load_product_component(api_manager.product[self.selected_row]['id'])

    def on_profile_tool_edit_clicked(self):
        """Редактирование инструмента профиля"""
        profile_tool = api_manager.profile_tool[self.selected_row]
        dialog = DialogEditProfileTool(profile_tool, self)
        if dialog.exec():
            self.refresh_data()
            self.load_profile_tool_component(api_manager.profile_tool[self.selected_row]['id'])

    def on_profile_tool_delete_clicked(self):
        """Удаление инструмента"""
        product = api_manager.profile_tool[self.selected_row]
        api_manager.api_profile_tool.delete_profile_tool(product['id'])
        self.refresh_data()


    def on_product_edit_clicked(self):
        """Редактирование изделия"""
        product = api_manager.product[self.selected_row]
        dialog = DialogEditProduct(product, self)
        if dialog.exec():
            self.refresh_data()
            self.load_product_component(api_manager.product[self.selected_row]['id'])

    def on_product_delete_clicked(self):
        """Удаление изделия"""
        product = api_manager.product[self.selected_row]
        api_manager.api_product.delete_product(product['id'])
        self.refresh_data()

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