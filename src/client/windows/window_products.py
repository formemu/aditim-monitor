"""
Содержимое изделий для ADITIM Monitor Client с вкладками и компонентами
"""

from PySide6.QtWidgets import QWidget, QMessageBox, QTableWidgetItem, QAbstractItemView, QDialog
from PySide6.QtCore import QFile, Qt, QTimer
from PySide6.QtUiTools import QUiLoader

from ..constants import UI_PATHS_ABS as UI_PATHS, get_style_path
from ..api_client import ApiClient
from ..style_utils import load_styles_with_constants
from ..async_utils import run_async
from ..references_manager import references_manager
from ..widgets.dialog_create_profile_tool import DialogCreateProfileTool


class ProductsContent(QWidget):
    """Виджет содержимого изделий с вкладками"""
    
    def __init__(self, api_client: ApiClient = None):
        super().__init__()
        self.api_client = api_client or ApiClient()
        
        # Больше не нужно кэшировать справочники - используем references_manager
        self.current_product_id = None  # ID текущего выбранного изделия
        self.current_tool_id = None  # ID текущего выбранного инструмента профиля
        
        # Кэш данных для предотвращения ненужных обновлений
        self.current_tools_data = None  # Изначально None для принудительной загрузки
        self.current_products_data = None
        
        self.load_ui()
        self.setup_ui()
        # Убираем загрузку справочников - они уже загружены в references_manager
        # self.load_departments()
        # self.load_profiles()
        # Не загружаем данные сразу, пусть таймер сработает при первой активации

    def load_ui(self):
        """Загрузка UI из файла"""
        ui_file = QFile(UI_PATHS["PRODUCTS_CONTENT"])
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
        
        # Подключение кнопок для инструментов профилей
        self.ui.pushButton_profile_tool_add.clicked.connect(self.on_profile_tool_add_clicked)
        self.ui.pushButton_profile_tool_edit.clicked.connect(self.on_profile_tool_edit_clicked)
        self.ui.pushButton_profile_tool_delete.clicked.connect(self.on_profile_tool_delete_clicked)
        self.ui.tableWidget_profile_tools.itemSelectionChanged.connect(self.on_profile_tool_selection_changed)
        self.ui.lineEdit_search_profile_tools.textChanged.connect(self.on_profile_tools_search_changed)
        
        # Подключение кнопок для изделий
        self.ui.pushButton_product_add.clicked.connect(self.on_product_add_clicked)
        self.ui.pushButton_product_edit.clicked.connect(self.on_product_edit_clicked)
        self.ui.pushButton_product_delete.clicked.connect(self.on_product_delete_clicked)
        self.ui.tableWidget_products.itemSelectionChanged.connect(self.on_product_selection_changed)
        self.ui.lineEdit_search_products.textChanged.connect(self.on_products_search_changed)
        
        # Подключение кнопок для компонентов
        self.ui.pushButton_component_add.clicked.connect(self.on_component_add_clicked)
        self.ui.pushButton_component_edit.clicked.connect(self.on_component_edit_clicked)
        self.ui.pushButton_component_delete.clicked.connect(self.on_component_delete_clicked)
        self.ui.tableWidget_components.itemSelectionChanged.connect(self.on_component_selection_changed)
        
        # Подключение сигнала переключения вкладок
        self.ui.tabWidget_products.currentChanged.connect(self.on_tab_changed)
        
        # Настройка таблиц
        self.setup_tables()
        
        # Настройка автоматического обновления каждые 5 секунд с умной проверкой
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.load_current_tab_data_async)
        # НЕ запускаем таймер сразу, он будет запущен при активации окна
        # self.update_timer.start(5000)  # 5000 мс = 5 секунд

    def setup_tables(self):
        """Настройка параметров таблиц"""
        # Таблица инструментов профилей (убраны ненужные колонки)
        self.ui.tableWidget_profile_tools.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ui.tableWidget_profile_tools.setSelectionMode(QAbstractItemView.SingleSelection)
        self.ui.tableWidget_profile_tools.setFocusPolicy(Qt.NoFocus)
        self.ui.tableWidget_profile_tools.setColumnWidth(0, 200)  # Профиль
        self.ui.tableWidget_profile_tools.horizontalHeader().setStretchLastSection(True)  # Описание
        
        # Таблица изделий
        self.ui.tableWidget_products.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ui.tableWidget_products.setSelectionMode(QAbstractItemView.SingleSelection)
        self.ui.tableWidget_products.setFocusPolicy(Qt.NoFocus)
        self.ui.tableWidget_products.setColumnWidth(0, 200)  # Название
        self.ui.tableWidget_products.setColumnWidth(1, 150)  # Департамент
        self.ui.tableWidget_products.horizontalHeader().setStretchLastSection(True)  # Описание
        
        # Таблица компонентов
        self.ui.tableWidget_components.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ui.tableWidget_components.setSelectionMode(QAbstractItemView.SingleSelection)
        self.ui.tableWidget_components.setFocusPolicy(Qt.NoFocus)
        self.ui.tableWidget_components.setColumnWidth(0, 300)  # Название
        self.ui.tableWidget_components.horizontalHeader().setStretchLastSection(True)  # Количество

    def refresh_data(self):
        """Публичный метод для принудительного обновления данных"""
        self.current_tools_data = []  # Сбрасываем кэш
        self.current_products_data = []
        self.load_data()

    def load_data(self):
        """Загружает все данные с сервера"""
        self.load_profile_tools_from_server()
        self.load_products_from_server()

    def load_profile_tools_from_server(self):
        """Загружает инструменты профилей с сервера"""
        try:
            tools = self.api_client.get_profile_tools()
            self.update_tools_table(tools)
                
        except Exception as e:
            QMessageBox.warning(self, "Предупреждение", f"Не удалось загрузить инструменты профилей с сервера: {e}")

    def update_tools_table(self, tools):
        """Обновляет таблицу инструментов с проверкой изменений"""
        # Проверяем если таблица пустая - обновляем принудительно
        is_table_empty = self.ui.tableWidget_profile_tools.rowCount() == 0
        
        # Сравниваем новые данные с кэшем (None означает первую загрузку)
        if self.current_tools_data is not None and tools == self.current_tools_data and not is_table_empty:
            return  # Данные не изменились и таблица не пустая, не обновляем
        
        # Сохраняем текущее выделение
        current_selection = None
        selected_items = self.ui.tableWidget_profile_tools.selectedItems()
        if selected_items:
            current_selection = selected_items[0].row()
        
        # Обновляем кэш
        self.current_tools_data = tools
        
        # Очищаем таблицу
        self.ui.tableWidget_profile_tools.setRowCount(0)
        
        # Заполняем таблицу данными с сервера (убраны названия и департамент)
        self.ui.tableWidget_profile_tools.setRowCount(len(tools))
        
        for row, tool in enumerate(tools):
            # Профиль (размерность + артикул профиля)
            profile_text = f"{tool.get('dimension', 'Неизвестно')} - {tool.get('profile_article', 'Неизвестно')}"
            profile_item = QTableWidgetItem(profile_text)
            profile_item.setFlags(profile_item.flags() & ~Qt.ItemIsEditable)
            profile_item.setData(Qt.UserRole, tool.get('id'))  # Сохраняем ID инструмента
            self.ui.tableWidget_profile_tools.setItem(row, 0, profile_item)
            
            # Описание
            description_item = QTableWidgetItem(tool.get('description', ''))
            description_item.setFlags(description_item.flags() & ~Qt.ItemIsEditable)
            self.ui.tableWidget_profile_tools.setItem(row, 1, description_item)
        
        # Восстанавливаем выделение если возможно
        if current_selection is not None and current_selection < len(tools):
            self.ui.tableWidget_profile_tools.selectRow(current_selection)

    def load_products_from_server(self):
        """Загружает изделия с сервера"""
        try:
            products = self.api_client.get_products()
            self.update_products_table(products)
                
        except Exception as e:
            QMessageBox.warning(self, "Предупреждение", f"Не удалось загрузить изделия с сервера: {e}")

    def update_products_table(self, products):
        """Обновляет таблицу изделий с проверкой изменений"""
        # Проверяем если таблица пустая - обновляем принудительно
        is_table_empty = self.ui.tableWidget_products.rowCount() == 0
        
        # Сравниваем новые данные с кэшем (None означает первую загрузку)
        if self.current_products_data is not None and products == self.current_products_data and not is_table_empty:
            return  # Данные не изменились и таблица не пустая, не обновляем
        
        # Сохраняем текущее выделение
        current_selection = None
        selected_items = self.ui.tableWidget_products.selectedItems()
        if selected_items:
            current_selection = selected_items[0].row()
        
        # Обновляем кэш
        self.current_products_data = products
        
        # Очищаем таблицу
        self.ui.tableWidget_products.setRowCount(0)
        
        # Заполняем таблицу данными с сервера
        self.ui.tableWidget_products.setRowCount(len(products))
        
        for row, product in enumerate(products):
            # Название
            name_item = QTableWidgetItem(product.get('name', ''))
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
            name_item.setData(Qt.UserRole, product.get('id'))  # Сохраняем ID изделия
            self.ui.tableWidget_products.setItem(row, 0, name_item)
            
            # Департамент (используем references_manager)
            dept_id = product.get('id_departament', 0)
            departments = references_manager.get_departments()
            dept_name = departments.get(dept_id, 'Неизвестно')
            dept_item = QTableWidgetItem(dept_name)
            dept_item.setFlags(dept_item.flags() & ~Qt.ItemIsEditable)
            self.ui.tableWidget_products.setItem(row, 1, dept_item)
            
            # Описание
            description_item = QTableWidgetItem(product.get('description', ''))
            description_item.setFlags(description_item.flags() & ~Qt.ItemIsEditable)
            self.ui.tableWidget_products.setItem(row, 2, description_item)
        
        # Восстанавливаем выделение если возможно
        if current_selection is not None and current_selection < len(products):
            self.ui.tableWidget_products.selectRow(current_selection)

    def load_components(self, item_type: str, item_id: int):
        """Загружает компоненты для выбранного элемента"""
        try:
            if item_type == "product":
                components = self.api_client.get_product_components(item_id)
                self.ui.label_selected_item.setText(f"Изделие ID: {item_id}")
            elif item_type == "profile_tool":
                components = self.api_client.get_profile_tool_components(item_id)
                self.ui.label_selected_item.setText(f"Инструмент ID: {item_id}")
            else:
                return
            
            # Очищаем таблицу компонентов
            self.ui.tableWidget_components.setRowCount(0)
            
            if not components:
                self.ui.label_component_description.setText("Описание: -")
                return
            
            # Заполняем таблицу компонентов
            self.ui.tableWidget_components.setRowCount(len(components))
            
            for row, component in enumerate(components):
                if item_type == "product":
                    # Для изделий
                    name_item = QTableWidgetItem(component.get('component_name', ''))
                    quantity_item = QTableWidgetItem(str(component.get('quantity', 1)))
                else:
                    # Для инструментов профилей
                    comp_type = component.get('component_type', '')
                    variant = component.get('variant')
                    name = f"{comp_type}" + (f" (вариант {variant})" if variant else "")
                    name_item = QTableWidgetItem(name)
                    quantity_item = QTableWidgetItem(component.get('status', ''))
                
                name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
                name_item.setData(Qt.UserRole, component.get('id'))  # Сохраняем ID компонента
                quantity_item.setFlags(quantity_item.flags() & ~Qt.ItemIsEditable)
                
                self.ui.tableWidget_components.setItem(row, 0, name_item)
                self.ui.tableWidget_components.setItem(row, 1, quantity_item)
            
            # Включаем кнопки управления компонентами
            self.ui.pushButton_component_add.setEnabled(True)
            
        except Exception as e:
            QMessageBox.warning(self, "Предупреждение", f"Не удалось загрузить компоненты: {e}")

    def load_data_async(self):
        """Асинхронная загрузка данных с сервера"""
        run_async(
            self.api_client.get_profile_tools,
            on_success=self.on_profile_tools_loaded,
            on_error=self.on_data_load_error
        )
        run_async(
            self.api_client.get_products,
            on_success=self.on_products_loaded,
            on_error=self.on_data_load_error
        )

    def load_current_tab_data_async(self):
        """Контекстно-зависимая загрузка данных для активной вкладки"""
        # Проверяем что виджет и окно доступны
        if not hasattr(self, 'ui') or not self.ui:
            return
            
        current_tab_index = self.ui.tabWidget_products.currentIndex()
        
        # 0 - Инструменты профилей, 1 - Изделия
        if current_tab_index == 0:
            # Загружаем только инструменты профилей
            try:
                tools = self.api_client.get_profile_tools()
                self.on_profile_tools_loaded(tools)
            except Exception as e:
                self.on_data_load_error(e)
        elif current_tab_index == 1:
            # Загружаем только изделия
            try:
                products = self.api_client.get_products()
                self.on_products_loaded(products)
            except Exception as e:
                self.on_data_load_error(e)

    def on_tab_changed(self, index):
        """Обработчик смены вкладки"""
        # При смене вкладки не загружаем данные автоматически
        # Данные будут загружены только по таймеру для активной вкладки
        pass

    def on_profile_tools_loaded(self, tools):
        """Обработчик успешной загрузки инструментов профилей"""
        try:
            self.update_tools_table(tools)
        except Exception as e:
            print(f"Ошибка обновления таблицы инструментов: {e}")

    def on_products_loaded(self, products):
        """Обработчик успешной загрузки изделий"""
        try:
            self.update_products_table(products)
        except Exception as e:
            print(f"Ошибка обновления таблицы изделий: {e}")

    def on_data_load_error(self, error):
        """Обработчик ошибки загрузки данных"""
        print(f"Ошибка загрузки данных: {error}")

    # Обработчики событий для инструментов профилей
    def on_profile_tool_selection_changed(self):
        """Обработчик изменения выделения в таблице инструментов профилей"""
        selected_items = self.ui.tableWidget_profile_tools.selectedItems()
        if selected_items:
            row = selected_items[0].row()
            tool_id = self.ui.tableWidget_profile_tools.item(row, 0).data(Qt.UserRole)
            self.current_tool_id = tool_id
            self.current_product_id = None  # Сброс выбора изделия
            
            # Сброс выделения в таблице изделий
            self.ui.tableWidget_products.setCurrentItem(None)
            
            # Загружаем компоненты инструмента
            self.load_components("profile_tool", tool_id)
        else:
            self.current_tool_id = None
            self.clear_components()

    def on_profile_tool_add_clicked(self):
        """Обработчик кнопки добавления инструмента профиля"""
        try:
            dialog = DialogCreateProfileTool(self.api_client, self)
            dialog.profile_tool_created.connect(self.on_profile_tool_created)
            
            if dialog.exec() == QDialog.Accepted:
                # Диалог уже обновляет данные через сигнал
                pass
                
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось открыть диалог создания инструмента: {e}")

    def on_profile_tool_created(self, tool_data):
        """Обработчик успешного создания инструмента профиля"""
        # Обновляем таблицу инструментов
        self.load_profile_tools_from_server()
        
        QMessageBox.information(
            self, 
            "Успех", 
            f"Инструмент профиля успешно создан и добавлен в список!"
        )

    def on_profile_tool_edit_clicked(self):
        """Обработчик кнопки редактирования инструмента профиля"""
        QMessageBox.information(self, "Информация", "Функция будет реализована позже")

    def on_profile_tool_delete_clicked(self):
        """Обработчик кнопки удаления инструмента профиля"""
        QMessageBox.information(self, "Информация", "Функция будет реализована позже")

    def on_profile_tools_search_changed(self, text):
        """Обработчик изменения поиска для инструментов профилей"""
        # Простая фильтрация по названию
        for row in range(self.ui.tableWidget_profile_tools.rowCount()):
            item = self.ui.tableWidget_profile_tools.item(row, 0)
            if item:
                visible = text.lower() in item.text().lower()
                self.ui.tableWidget_profile_tools.setRowHidden(row, not visible)

    # Обработчики событий для изделий
    def on_product_selection_changed(self):
        """Обработчик изменения выделения в таблице изделий"""
        selected_items = self.ui.tableWidget_products.selectedItems()
        if selected_items:
            row = selected_items[0].row()
            product_id = self.ui.tableWidget_products.item(row, 0).data(Qt.UserRole)
            self.current_product_id = product_id
            self.current_tool_id = None  # Сброс выбора инструмента
            
            # Сброс выделения в таблице инструментов
            self.ui.tableWidget_profile_tools.setCurrentItem(None)
            
            # Загружаем компоненты изделия
            self.load_components("product", product_id)
        else:
            self.current_product_id = None
            self.clear_components()

    def on_product_add_clicked(self):
        """Обработчик кнопки добавления изделия"""
        QMessageBox.information(self, "Информация", "Функция будет реализована позже")

    def on_product_edit_clicked(self):
        """Обработчик кнопки редактирования изделия"""
        QMessageBox.information(self, "Информация", "Функция будет реализована позже")

    def on_product_delete_clicked(self):
        """Обработчик кнопки удаления изделия"""
        QMessageBox.information(self, "Информация", "Функция будет реализована позже")

    def on_products_search_changed(self, text):
        """Обработчик изменения поиска для изделий"""
        # Простая фильтрация по названию
        for row in range(self.ui.tableWidget_products.rowCount()):
            item = self.ui.tableWidget_products.item(row, 0)
            if item:
                visible = text.lower() in item.text().lower()
                self.ui.tableWidget_products.setRowHidden(row, not visible)

    # Обработчики событий для компонентов
    def on_component_selection_changed(self):
        """Обработчик изменения выделения в таблице компонентов"""
        selected_items = self.ui.tableWidget_components.selectedItems()
        if selected_items:
            row = selected_items[0].row()
            component_id = self.ui.tableWidget_components.item(row, 0).data(Qt.UserRole)
            
            # Показываем описание компонента (если есть)
            if self.current_product_id:
                try:
                    components = self.api_client.get_product_components(self.current_product_id)
                    component = next((c for c in components if c.get('id') == component_id), None)
                    if component:
                        self.ui.label_component_description.setText(f"Описание: {component.get('description', '-')}")
                except:
                    pass
            elif self.current_tool_id:
                try:
                    components = self.api_client.get_profile_tool_components(self.current_tool_id)
                    component = next((c for c in components if c.get('id') == component_id), None)
                    if component:
                        self.ui.label_component_description.setText(f"Описание: {component.get('description', '-')}")
                except:
                    pass
            
            # Включаем кнопки редактирования и удаления
            self.ui.pushButton_component_edit.setEnabled(True)
            self.ui.pushButton_component_delete.setEnabled(True)
        else:
            self.ui.label_component_description.setText("Описание: -")
            self.ui.pushButton_component_edit.setEnabled(False)
            self.ui.pushButton_component_delete.setEnabled(False)

    def on_component_add_clicked(self):
        """Обработчик кнопки добавления компонента"""
        QMessageBox.information(self, "Информация", "Функция будет реализована позже")

    def on_component_edit_clicked(self):
        """Обработчик кнопки редактирования компонента"""
        QMessageBox.information(self, "Информация", "Функция будет реализована позже")

    def on_component_delete_clicked(self):
        """Обработчик кнопки удаления компонента"""
        QMessageBox.information(self, "Информация", "Функция будет реализована позже")

    def clear_components(self):
        """Очищает панель компонентов"""
        self.ui.tableWidget_components.setRowCount(0)
        self.ui.label_selected_item.setText("Выберите изделие")
        self.ui.label_component_description.setText("Описание: -")
        self.ui.pushButton_component_add.setEnabled(False)
        self.ui.pushButton_component_edit.setEnabled(False)
        self.ui.pushButton_component_delete.setEnabled(False)

    def start_auto_refresh(self):
        """Запускает автоматическое обновление данных"""
        if not self.update_timer.isActive():
            self.update_timer.start(5000)  # 5 секунд
            # Сразу загружаем данные при активации
            self.load_current_tab_data_async()

    def stop_auto_refresh(self):
        """Останавливает автоматическое обновление данных"""
        if self.update_timer.isActive():
            self.update_timer.stop()
