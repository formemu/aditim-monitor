"""
Содержимое изделий для ADITIM Monitor Client с вкладками и компонентами
"""
from PySide6.QtWidgets import QWidget, QMessageBox, QTableWidgetItem, QAbstractItemView, QHeaderView
from PySide6.QtCore import QFile, Qt, QTimer
from PySide6.QtUiTools import QUiLoader
from ..constant import UI_PATHS_ABS as UI_PATHS, get_style_path
from ..api.api_product import ApiProduct
from ..api.api_profile_tool import ApiProfileTool
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
        self.api_product = ApiProduct()
        self.api_profile_tool = ApiProfileTool()
        self.profile_tool_data = None # Кэш данных инструментов
        self.product_data = None # Кэш данных изделий
        self.tab_index = 0  # Индекс текущей вкладки
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
    def load_data_from_server(self):
        """Загрузка всех данных"""
        if self.tab_index == 0:
            tool = self.api_profile_tool.get_profile_tool()
            self.profile_tool_data = tool
            self.update_table_tool(tool)
            
        elif self.tab_index == 1:
            product = self.api_product.get_product()
            self.product_data = product
            self.update_table_product(product)

    def refresh_data(self):
        """Принудительное обновление данных"""
        if self.tab_index == 0:
            self.profile_tool_data = []
            self.load_data_from_server()
        elif self.tab_index == 1:
            self.product_data = []
            self.load_data_from_server()

    def on_tab_changed(self):
        """Обработчик смены вкладки — обновляет данные для выбранной вкладки"""
        self.tab_index = self.ui.tabWidget_products.currentIndex()
        self.refresh_data()
        self.clear_component()
    
    # =============================================================================
    # ОТОБРАЖЕНИЕ ДАННЫХ: ТАБЛИЦЫ И ИНФОРМАЦИОННЫЕ ПАНЕЛИ
    # =============================================================================
    def update_table_tool(self, list_tool):
        """Обновление таблицы инструментов профиля с корректным отображением и заполнением по ширине"""
        table = self.ui.tableWidget_profile_tool
        table.setRowCount(len(list_tool))
        table.setColumnCount(2)
        # Заголовки столбцов
        table.setHorizontalHeaderLabels(["Размер и профиль", "Описание"])
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        for row, tool in enumerate(list_tool):
            # Размер и профиль
            name = f"{tool.get('dimension')} - {tool.get('profile_article')}"
            table.setItem(row, 0, QTableWidgetItem(name))
            # Описание
            description = tool.get('description')
            table.setItem(row, 1, QTableWidgetItem(description))

    def update_table_product(self, list_product):
        """Обновление таблицы изделий с корректным отображением и заполнением по ширине"""
        table = self.ui.tableWidget_product
        table.setRowCount(len(list_product))
        table.setColumnCount(3)
        # Заголовки столбцов
        table.setHorizontalHeaderLabels(["Название", "Департамент", "Описание"])
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        for row, product in enumerate(list_product):
            # Название изделия
            name = product.get('name')
            table.setItem(row, 0, QTableWidgetItem(name))
            # Департамент
            dept = product.get('departament')
            table.setItem(row, 1, QTableWidgetItem(dept))
            # Описание
            desc = product.get('description')
            table.setItem(row, 2, QTableWidgetItem(desc))

    def load_component(self, item_id: int):
        """Загрузка компонентов элемента"""
        if self.tab_index == 1:
            api = self.api_product
            list_component = api.get_product_component(item_id)
        else:
            api = self.api_profile_tool
            list_component = api.get_profile_tool_component(item_id)

        self.ui.label_selected_item.setText(f"ID: {item_id}")
        self.ui.tableWidget_component.setRowCount(0)
        self.ui.tableWidget_component.setRowCount(len(list_component))

        for row, comp in enumerate(list_component):
            if self.tab_index == 1:
                name = comp.get('component_name')
                qty = comp.get('quantity')
            else:
                name = comp.get('variant_id')
                qty = comp.get('status', '')
            name_item = QTableWidgetItem(name)
            name_item.setData(Qt.UserRole, comp.get('id'))
            qty_item = QTableWidgetItem(qty)
            self.ui.tableWidget_component.setItem(row, 0, name_item)
            self.ui.tableWidget_component.setItem(row, 1, qty_item)
        self.ui.pushButton_component_add.setEnabled(True)

    def clear_component(self):
        """Очистка панели компонентов"""
        self.ui.tableWidget_component.setRowCount(0)
        self.ui.label_selected_item.setText("Выберите изделие")
        self.ui.label_component_description.setText("Описание: -")
        self.ui.pushButton_component_add.setEnabled(False)
        self.ui.pushButton_component_edit.setEnabled(False)
        self.ui.pushButton_component_delete.setEnabled(False)

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
    # ОБРАБОТЧИКИ СОБЫТИЙ
    # =============================================================================
    def on_selection_changed(self):
        """Обработчик выбора элемента"""
        row = self.get_selected_row()
        if row is not None:
            if self.tab_index == 0:
                profile = self.profile_tool_data[row]
                self.load_component(profile.get('id'))
            else:
                product = self.product_data[row]
                self.load_component(product.get('id'))

    def get_selected_row(self):
        """Возвращает индекс выбранной строки или None"""
        if self.tab_index == 0:
            selected = self.ui.tableWidget_profile_tool.selectedItems()
        else:
            selected = self.ui.tableWidget_product.selectedItems()
        return selected[0].row() if selected else None
    
    def load_data_by_tab(self):
        """Загрузка данных и компонентов в зависимости от выбранной вкладки"""

        if self.tab_index == 0:
            # Вкладка инструмент
            list_tool = self.api_profile_tool.get_profile_tool()
            self.update_table_tool(list_tool)

        elif self.tab_index == 1:
            # Вкладка изделие
            list_product = self.api_product.get_product()
            self.update_table_product(list_product)

    # =============================================================================
    # ОБРАБОТЧИКИ СОБЫТИЙ: УПРАВЛЕНИЕ
    # =============================================================================
    def on_profile_tool_add_clicked(self):
        """Добавление инструмента профиля"""
        dialog = DialogCreateProfileTool(self)
        dialog.profile_tool_created.connect(self.refresh_data)
        dialog.exec()

    def on_product_add_clicked(self):
        """Добавление изделия"""
        dialog = DialogCreateProduct(self)
        dialog.product_created.connect(self.refresh_data)
        dialog.exec()


    def on_profile_tool_edit_clicked(self):
        """Редактирование инструмента профиля"""
        row = self.get_selected_row()
        profile_tool = self.profile_tool_data[row]
        dialog = DialogEditProfileTool(profile_tool, self)
        dialog.profile_tool_updated.connect(self.refresh_data)
        dialog.exec()

    def on_profile_tool_delete_clicked(self):
        """Удаление инструмента"""
        row = self.get_selected_row()
        task = self.profile_tool_data[row]
        self.api_profile_tool.delete_profile_tool(task['id'])
        self.refresh_data()

    def on_product_edit_clicked(self):
        """Редактирование изделия"""
        row = self.get_selected_row()
        product = self.product_data[row]
        dialog = DialogEditProduct(product, self)
        dialog.product_updated.connect(self.refresh_data)
        dialog.exec()

    def on_product_delete_clicked(self):
        """Удаление изделия"""
        row = self.get_selected_row()
        task = self.product_data[row]
        self.api_product.delete_product(task['id'])
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
            self.load_data_from_server()

    def stop_auto_refresh(self):
        """Остановка автообновления"""
        if self.update_timer.isActive():
            self.update_timer.stop()