"""
Содержимое изделий для ADITIM Monitor Client с вкладками и компонентами
"""
from PySide6.QtWidgets import QWidget, QMessageBox, QTableWidgetItem, QAbstractItemView
from PySide6.QtCore import QFile, Qt, QTimer
from PySide6.QtUiTools import QUiLoader
from ..constant import UI_PATHS_ABS as UI_PATHS, get_style_path
from ..api.api_product import ApiProduct
from ..api.api_profile_tool import ApiProfileTool
from ..style_util import load_styles
from ..references_manager import references_manager
from ..widgets.dialog_create_profile_tool import DialogCreateProfileTool
from ..widgets.dialog_create_product import DialogCreateProduct


class WindowProduct(QWidget):
    """Виджет содержимого изделий с вкладками"""
    def __init__(self):
        super().__init__()
        self.api_product = ApiProduct()
        self.api_profile_tool = ApiProfileTool()
        self.current_product_id = None
        self.current_tool_id = None
        self.current_data_tool = None
        self.current_data_product = None
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
        self.ui.tableWidget_component.itemSelectionChanged.connect(self.on_component_selection_changed)
        self.ui.tabWidget_products.currentChanged.connect(self.on_tab_changed)
        # Подключения: профили
        self.ui.pushButton_profile_tool_add.clicked.connect(self.on_profile_tool_add_clicked)
        self.ui.pushButton_profile_tool_edit.clicked.connect(self.on_profile_tool_edit_clicked)
        self.ui.pushButton_profile_tool_delete.clicked.connect(self.on_profile_tool_delete_clicked)
        self.ui.tableWidget_profile_tool.itemSelectionChanged.connect(self.on_profile_tool_selection_changed)
        self.ui.lineEdit_search_profile_tool.textChanged.connect(lambda text: self._filter_table(self.ui.tableWidget_profile_tool, text.lower()))
        # Подключения: изделия
        self.ui.pushButton_product_add.clicked.connect(self.on_product_add_clicked)
        self.ui.pushButton_product_edit.clicked.connect(self.on_product_edit_clicked)
        self.ui.pushButton_product_delete.clicked.connect(self.on_product_delete_clicked)
        self.ui.tableWidget_product.itemSelectionChanged.connect(self.on_product_selection_changed)
        self.ui.lineEdit_search_product.textChanged.connect(lambda text: self._filter_table(self.ui.tableWidget_product, text.lower()))
        self.setup_tables()
        # Таймер автообновления
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.load_current_tab_data)

    def setup_tables(self):
        """Настройка таблиц"""
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

    # =============================================================================
    # УПРАВЛЕНИЕ ДАННЫМИ: ЗАГРУЗКА И ОБНОВЛЕНИЕ
    # =============================================================================
    def refresh_data(self):
        """Принудительное обновление данных"""
        self.current_data_tool = []
        self.current_data_product = []
        self.load_data()

    def load_data(self):
        """Загрузка всех данных"""
        try:
            list_tool = self.api_profile_tool.get_profile_tool()
            self.update_table_tool(list_tool)
        except Exception as e:
            QMessageBox.warning(self, "Предупреждение", f"Ошибка загрузки инструментов: {e}")
        try:
            list_product = self.api_product.get_product()
            self.update_table_product(list_product)
        except Exception as e:
            QMessageBox.warning(self, "Предупреждение", f"Ошибка загрузки изделий: {e}")

    def load_current_tab_data(self):
        """Загрузка данных для текущей вкладки"""
        index = self.ui.tabWidget_products.currentIndex()
        if index == 0:
            self.load_data()
        elif index == 1:
            self.load_data()

    def update_table_tool(self, list_tool):
        """Обновление таблицы инструментов профилей"""
        if self.current_data_tool == list_tool and self.ui.tableWidget_profile_tool.rowCount() > 0:
            return
        self.current_data_tool = list_tool
        table = self.ui.tableWidget_profile_tool
        table.setRowCount(len(list_tool))
        for row, tool in enumerate(list_tool):
            # Название инструмента
            name_item = QTableWidgetItem(f"{tool.get('dimension', 'Неизвестно')} - {tool.get('profile_article', 'Неизвестно')}")
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
            name_item.setData(Qt.UserRole, tool.get('id'))
            table.setItem(row, 0, name_item)
            # Описание
            desc_item = QTableWidgetItem(tool.get('description', ''))
            desc_item.setFlags(desc_item.flags() & ~Qt.ItemIsEditable)
            table.setItem(row, 1, desc_item)

    def update_table_product(self, list_product):
        """Обновление таблицы изделий"""
        if self.current_data_product == list_product and self.ui.tableWidget_product.rowCount() > 0:
            return
        self.current_data_product = list_product
        table = self.ui.tableWidget_product
        table.setRowCount(len(list_product))
        dict_department = references_manager.get_department()
        for row, product in enumerate(list_product):
            # Название изделия
            name_item = QTableWidgetItem(product.get('name', ''))
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
            name_item.setData(Qt.UserRole, product.get('id'))
            table.setItem(row, 0, name_item)
            # Департамент
            dept_item = QTableWidgetItem(dict_department.get(product.get('department_id', 0), 'Неизвестно'))
            dept_item.setFlags(dept_item.flags() & ~Qt.ItemIsEditable)
            table.setItem(row, 1, dept_item)
            # Описание
            desc_item = QTableWidgetItem(product.get('description', ''))
            desc_item.setFlags(desc_item.flags() & ~Qt.ItemIsEditable)
            table.setItem(row, 2, desc_item)

    # =============================================================================
    # РАБОТА С КОМПОНЕНТАМИ
    # =============================================================================
    def load_component(self, item_type: str, item_id: int):
        """Загрузка компонентов элемента"""
        api = self.api_product if item_type == "product" else self.api_profile_tool
        method = api.get_product_component if item_type == "product" else api.get_profile_tool_component
        list_component = method(item_id)
        self.ui.label_selected_item.setText(f"{item_type.capitalize()} ID: {item_id}")
        self.ui.tableWidget_component.setRowCount(0)
        if not list_component:
            self.ui.label_component_description.setText("Описание: -")
            return
        self.ui.tableWidget_component.setRowCount(len(list_component))
        for row, comp in enumerate(list_component):
            if item_type == "product":
                name = comp.get('component_name', '')
                qty = str(comp.get('quantity', 1))
            else:
                name = f"{comp.get('component_type', '')}" + (f" (вариант {comp.get('variant')})" if comp.get('variant') else "")
                qty = comp.get('status', '')
            name_item = QTableWidgetItem(name)
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
            name_item.setData(Qt.UserRole, comp.get('id'))
            qty_item = QTableWidgetItem(qty)
            qty_item.setFlags(qty_item.flags() & ~Qt.ItemIsEditable)
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

    # =============================================================================
    # ОБРАБОТЧИКИ СОБЫТИЙ
    # =============================================================================
    def on_tab_changed(self, index):
        """Обработчик смены вкладки"""
        pass  # Обновление по таймеру

    def on_profile_tool_selection_changed(self):
        """Обработчик изменения выделения в таблице инструментов профилей"""
        selected_items = self.ui.tableWidget_profile_tool.selectedItems()
        if selected_items:
            row = selected_items[0].row()
            tool_id = self.ui.tableWidget_profile_tool.item(row, 0).data(Qt.UserRole)
            self.current_tool_id = tool_id
            self.current_product_id = None  # Сброс выбора изделия
            # Сброс выделения в таблице изделий
            self.ui.tableWidget_product.setCurrentItem(None)
            # Загружаем компоненты инструмента
            self.load_component("profile_tool", tool_id)
        else:
            self.current_tool_id = None
            self.clear_component()

    def on_product_selection_changed(self):
        """Обработчик изменения выделения в таблице изделий"""
        selected_items = self.ui.tableWidget_product.selectedItems()
        if selected_items:
            row = selected_items[0].row()
            product_id = self.ui.tableWidget_product.item(row, 0).data(Qt.UserRole)
            self.current_product_id = product_id
            self.current_tool_id = None  # Сброс выбора инструмента
            # Сброс выделения в таблице инструментов
            self.ui.tableWidget_profile_tool.setCurrentItem(None)
            # Загружаем компоненты изделия
            self.load_component("product", product_id)
        else:
            self.current_product_id = None
            self.clear_component()

    def on_component_selection_changed(self):
        """Обработчик изменения выделения в таблице компонентов"""
        selected = self.ui.tableWidget_component.selectedItems()
        if selected:
            component_id = self.ui.tableWidget_component.item(selected[0].row(), 0).data(Qt.UserRole)
            api = self.api_product if self.current_product_id else self.api_profile_tool
            method = api.get_product_component if self.current_product_id else api.get_profile_tool_component
            item_id = self.current_product_id or self.current_tool_id
            try:
                comp = next((c for c in method(item_id) if c.get('id') == component_id), None)
                if comp:
                    self.ui.label_component_description.setText(f"Описание: {comp.get('description', '-')}")
            except:
                pass
            self.ui.pushButton_component_edit.setEnabled(True)
            self.ui.pushButton_component_delete.setEnabled(True)
        else:
            self.ui.label_component_description.setText("Описание: -")
            self.ui.pushButton_component_edit.setEnabled(False)
            self.ui.pushButton_component_delete.setEnabled(False)

    def _open_dialog(self, dialog_class, created_signal, callback):
        """Унифицированное открытие диалога"""
        try:
            dialog = dialog_class(self)
            getattr(dialog, created_signal).connect(callback)
            dialog.exec()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось открыть диалог: {e}")

    def on_profile_tool_add_clicked(self):
        """Добавление инструмента профиля"""
        self._open_dialog(DialogCreateProfileTool, 'profile_tool_created', self.on_profile_tool_created)

    def on_product_add_clicked(self):
        """Добавление изделия"""
        self._open_dialog(DialogCreateProduct, 'product_created', self.on_product_created)

    def on_profile_tool_created(self, tool_data):
        """Обработка создания инструмента профиля"""
        self.load_data()
        QMessageBox.information(self, "Успех", "Инструмент профиля успешно создан!")

    def on_product_created(self, product_data):
        """Обработка создания изделия"""
        self.load_data()
        QMessageBox.information(self, "Успех", f"Изделие '{product_data.get('name', '')}' успешно создано!")

    def on_profile_tool_edit_clicked(self):
        """Редактирование инструмента профиля"""
        QMessageBox.information(self, "Информация", "Функция будет реализована позже")

    def on_profile_tool_delete_clicked(self):
        """Удаление инструмента профиля"""
        self._delete_item(self.ui.tableWidget_profile_tool, 0, 0, self.api_profile_tool.delete_profile_tool, "инструмент")

    def on_product_edit_clicked(self):
        """Редактирование изделия"""
        QMessageBox.information(self, "Информация", "Функция будет реализована позже")

    def on_product_delete_clicked(self):
        """Удаление изделия"""
        self._delete_item(self.ui.tableWidget_product, 0, 0, self.api_product.delete_product, "изделие")

    def _delete_item(self, table, id_col, name_col, delete_func, item_type):
        """Унифицированный метод удаления элемента"""
        selected = table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Удаление", f"Выберите {item_type}.")
            return
        row = selected[0].row()
        item_id = table.item(row, id_col).data(Qt.UserRole)
        item_name = table.item(row, name_col).text()
        reply = QMessageBox.question(
            self, "Подтверждение удаления",
            f"Вы уверены, что хотите удалить {item_type} '{item_name}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            try:
                delete_func(item_id)
                self.load_data()
                self.clear_component()
                QMessageBox.information(self, "Успех", f"{item_type.capitalize()} и его компоненты успешно удалены.")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось удалить: {e}")

    def on_component_add_clicked(self):
        """Добавление компонента"""
        QMessageBox.information(self, "Информация", "Функция будет реализована позже")

    def on_component_edit_clicked(self):
        """Редактирование компонента"""
        QMessageBox.information(self, "Информация", "Функция будет реализована позже")

    def on_component_delete_clicked(self):
        """Удаление компонента"""
        QMessageBox.information(self, "Информация", "Функция будет реализована позже")

    def _filter_table(self, table, text):
        """Фильтрация строк таблицы"""
        for row in range(table.rowCount()):
            item = table.item(row, 0)
            if item:
                visible = text.lower() in item.text().lower()
                table.setRowHidden(row, not visible)

    # =============================================================================
    # УПРАВЛЕНИЕ АВТООБНОВЛЕНИЕМ
    # =============================================================================
    def start_auto_refresh(self):
        """Запуск автообновления"""
        if not self.update_timer.isActive():
            self.update_timer.start(5000)
            self.load_data()

    def stop_auto_refresh(self):
        """Остановка автообновления"""
        if self.update_timer.isActive():
            self.update_timer.stop()