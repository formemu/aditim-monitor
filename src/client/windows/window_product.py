"""
Содержимое изделий для ADITIM Monitor Client с вкладками и компонентами
"""
from PySide6.QtWidgets import QWidget, QMessageBox, QTableWidgetItem, QAbstractItemView, QDialog
from PySide6.QtCore import QFile, Qt, QTimer
from PySide6.QtUiTools import QUiLoader
from ..constant import UI_PATHS_ABS as UI_PATHS, get_style_path
from ..api.api_product import ApiProduct
from ..api.api_profile_tool import ApiProfileTool
from ..style_util import load_styles_with_constants
from ..async_util import run_async
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

    def load_ui(self):
        ui_file = QFile(UI_PATHS["PRODUCT_CONTENT"])
        ui_file.open(QFile.ReadOnly)
        loader = QUiLoader()
        self.ui = loader.load(ui_file)
        ui_file.close()

    def setup_ui(self):
        style_path = get_style_path("MAIN")
        style_sheet = load_styles_with_constants(style_path)
        self.ui.setStyleSheet(style_sheet)

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
        self.ui.lineEdit_search_profile_tool.textChanged.connect(self.on_profile_tool_search_changed)

        # Подключения: изделия
        self.ui.pushButton_product_add.clicked.connect(self.on_product_add_clicked)
        self.ui.pushButton_product_edit.clicked.connect(self.on_product_edit_clicked)
        self.ui.pushButton_product_delete.clicked.connect(self.on_product_delete_clicked)
        self.ui.tableWidget_product.itemSelectionChanged.connect(self.on_product_selection_changed)
        self.ui.lineEdit_search_product.textChanged.connect(self.on_product_search_changed)

        self.setup_tables()

        # Таймер автообновления
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.load_current_tab_data_async)

    def setup_tables(self):
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

    def refresh_data(self):
        self.current_data_tool = []
        self.current_data_product = []
        self.load_data()

    def load_data(self):
        self.load_profile_tool_from_server()
        self.load_product_from_server()

    # =============================================================================
    # ЗАГРУЗКА ДАННЫХ (с кэшированием и обновлением)
    # =============================================================================

    def load_profile_tool_from_server(self):
        self._load_data_async(self.api_profile_tool.get_profile_tool, self.update_table_tool)

    def load_product_from_server(self):
        self._load_data_async(self.api_product.get_product, self.update_table_product)

    def _load_data_async(self, fetch_func, update_callback):
        try:
            data = fetch_func()
            update_callback(data)
        except Exception as e:
            QMessageBox.warning(self, "Предупреждение", f"Ошибка загрузки: {e}")

    def update_table_tool(self, list_tool):
        self._update_table(
            table=self.ui.tableWidget_profile_tool,
            data=list_tool,
            current_data_attr='current_data_tool',
            columns=[
                lambda tool: f"{tool.get('dimension', 'Неизвестно')} - {tool.get('profile_article', 'Неизвестно')}",
                lambda tool: tool.get('description', '')
            ],
            id_key='id'
        )

    def update_table_product(self, list_product):
        departments = references_manager.get_department()
        self._update_table(
            table=self.ui.tableWidget_product,
            data=list_product,
            current_data_attr='current_data_product',
            columns=[
                lambda p: p.get('name', ''),
                lambda p: departments.get(p.get('department_id', 0), 'Неизвестно'),
                lambda p: p.get('description', '')
            ],
            id_key='id'
        )

    def _update_table(self, table, data, current_data_attr, columns, id_key):
        current_data = getattr(self, current_data_attr)
        is_empty = table.rowCount() == 0
        if current_data is not None and data == current_data and not is_empty:
            return
        setattr(self, current_data_attr, data)
        table.setRowCount(0)
        table.setRowCount(len(data))
        for row, item in enumerate(data):
            for col_idx, col_func in enumerate(columns):
                item_widget = QTableWidgetItem(col_func(item))
                item_widget.setFlags(item_widget.flags() & ~Qt.ItemIsEditable)
                if col_idx == 0:
                    item_widget.setData(Qt.UserRole, item.get(id_key))
                table.setItem(row, col_idx, item_widget)
        if hasattr(self, 'saved_selection') and self.saved_selection < len(data):
            table.selectRow(self.saved_selection)
            self.saved_selection = None

    # =============================================================================
    # РАБОТА С КОМПОНЕНТАМИ
    # =============================================================================

    def load_component(self, item_type: str, item_id: int):
        try:
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
        except Exception as e:
            QMessageBox.warning(self, "Предупреждение", f"Не удалось загрузить компоненты: {e}")

    def clear_component(self):
        self.ui.tableWidget_component.setRowCount(0)
        self.ui.label_selected_item.setText("Выберите изделие")
        self.ui.label_component_description.setText("Описание: -")
        self.ui.pushButton_component_add.setEnabled(False)
        self.ui.pushButton_component_edit.setEnabled(False)
        self.ui.pushButton_component_delete.setEnabled(False)

    # =============================================================================
    # АВТООБНОВЛЕНИЕ
    # =============================================================================

    def load_current_tab_data_async(self):
        if not hasattr(self, 'ui') or not self.ui:
            return
        index = self.ui.tabWidget_products.currentIndex()
        if index == 0:
            self.load_profile_tool_from_server()
        elif index == 1:
            self.load_product_from_server()

    def start_auto_refresh(self):
        if not self.update_timer.isActive():
            self.update_timer.start(5000)
            self.load_current_tab_data_async()

    def stop_auto_refresh(self):
        if self.update_timer.isActive():
            self.update_timer.stop()

    # =============================================================================
    # ОБРАБОТЧИКИ СОБЫТИЙ
    # =============================================================================

    def on_tab_changed(self, index):
        pass  # Обновление по таймеру

    def _on_item_selected(self, table, id_col, current_id_attr, other_id_attr, item_type):
        selected = table.selectedItems()
        if selected:
            row = selected[0].row()
            item_id = table.item(row, id_col).data(Qt.UserRole)
            setattr(self, current_id_attr, item_id)
            setattr(self, other_id_attr, None)
            getattr(table, 'setCurrentItem', lambda x: None)(None)
            self.load_component(item_type, item_id)
        else:
            setattr(self, current_id_attr, None)
            self.clear_component()

    def on_profile_tool_selection_changed(self):
        self._on_item_selected(
            self.ui.tableWidget_profile_tool, 0, 'current_tool_id', 'current_product_id', 'profile_tool'
        )

    def on_product_selection_changed(self):
        self._on_item_selected(
            self.ui.tableWidget_product, 0, 'current_product_id', 'current_tool_id', 'product'
        )

    def on_component_selection_changed(self):
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
        try:
            dialog = dialog_class(self)
            getattr(dialog, created_signal).connect(callback)
            dialog.exec()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось открыть диалог: {e}")

    def on_profile_tool_add_clicked(self):
        self._open_dialog(DialogCreateProfileTool, 'profile_tool_created', self.on_profile_tool_created)

    def on_product_add_clicked(self):
        self._open_dialog(DialogCreateProduct, 'product_created', self.on_product_created)

    def on_profile_tool_created(self, tool_data):
        self.load_profile_tool_from_server()
        QMessageBox.information(self, "Успех", "Инструмент профиля успешно создан!")

    def on_product_created(self, product_data):
        self.load_product_from_server()
        QMessageBox.information(self, "Успех", f"Изделие '{product_data.get('name', '')}' успешно создано!")

    def on_profile_tool_edit_clicked(self):
        QMessageBox.information(self, "Информация", "Функция будет реализована позже")

    def on_profile_tool_delete_clicked(self):
        QMessageBox.information(self, "Информация", "Функция будет реализована позже")

    def on_product_edit_clicked(self):
        QMessageBox.information(self, "Информация", "Функция будет реализована позже")

    def on_product_delete_clicked(self):
        QMessageBox.information(self, "Информация", "Функция будет реализована позже")

    def on_component_add_clicked(self):
        QMessageBox.information(self, "Информация", "Функция будет реализована позже")

    def on_component_edit_clicked(self):
        QMessageBox.information(self, "Информация", "Функция будет реализована позже")

    def on_component_delete_clicked(self):
        QMessageBox.information(self, "Информация", "Функция будет реализована позже")

    def on_profile_tool_search_changed(self, text):
        self._filter_table(self.ui.tableWidget_profile_tool, text)

    def on_product_search_changed(self, text):
        self._filter_table(self.ui.tableWidget_product, text)

    def _filter_table(self, table, text):
        for row in range(table.rowCount()):
            item = table.item(row, 0)
            if item:
                visible = text.lower() in item.text().lower()
                table.setRowHidden(row, not visible)