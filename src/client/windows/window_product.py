"""Содержимое изделий для ADITIM Monitor Client с вкладками и компонентами"""
from PySide6.QtWidgets import QMessageBox, QDialog, QMenu
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QAction

from ..base_window import BaseWindow
from ..base_table import BaseTable
from ..constant import UI_PATHS_ABS
from ..api_manager import api_manager
from ..widgets.profiletool.dialog_create_profiletool import DialogCreateProfileTool
from ..widgets.profiletool.dialog_edit_profiletool import DialogEditProfileTool
from ..widgets.product.dialog_create_product import DialogCreateProduct
from ..widgets.product.dialog_edit_product import DialogEditProduct
from ..widgets.profiletool.dialog_create_profiletool_component import DialogCreateProfiletoolComponent


class WindowProduct(BaseWindow):
    """Виджет содержимого изделий с вкладками"""
    def __init__(self):
        self.profiletool = None
        self.product = None
        self.component_id = None
        super().__init__(UI_PATHS_ABS["PRODUCT_CONTENT"], api_manager)

    # =============================================================================
    # ИНИЦИАЛИЗАЦИЯ И ЗАГРУЗКА ИНТЕРФЕЙСА
    # =============================================================================
    def setup_ui(self):
        """Настройка UI компонентов"""
        self.apply_styles()
        self.load_logo()
        # Общие подключения
        self.ui.tabWidget_main.currentChanged.connect(self.refresh_data)
        # Подключения: инструменты профиля
        self.ui.pushButton_profiletool_add.clicked.connect(self.on_profiletool_add_clicked)
        self.ui.pushButton_profiletool_edit.clicked.connect(self.on_profiletool_edit_clicked)
        self.ui.pushButton_profiletool_delete.clicked.connect(self.on_profiletool_delete_clicked)
        self.ui.tableWidget_profiletool.itemClicked.connect(self.on_main_table_clicked)
        self.ui.lineEdit_search_profiletool.textChanged.connect(self.filter_table)
        # Подключения: изделия
        self.ui.pushButton_product_add.clicked.connect(self.on_product_add_clicked)
        self.ui.pushButton_product_edit.clicked.connect(self.on_product_edit_clicked)
        self.ui.pushButton_product_delete.clicked.connect(self.on_product_delete_clicked)
        self.ui.tableWidget_product.itemClicked.connect(self.on_main_table_clicked)
        self.ui.lineEdit_search_product.textChanged.connect(self.filter_table)

        # Подключение компонентов
        self.ui.pushButton_component_add.clicked.connect(self.on_component_add_clicked)
        self.ui.pushButton_component_delete.clicked.connect(self.on_component_delete_clicked)
        self.ui.tableWidget_component.itemClicked.connect(self.on_component_clicked)

        # Инициализация таблицы
        self.refresh_data()

    # =============================================================================
    # УПРАВЛЕНИЕ ДАННЫМИ: ЗАГРУЗКА И ОБНОВЛЕНИЕ
    # =============================================================================
    def refresh_data(self):
        """Принудительное обновление данных"""
        self.profiletool = None
        self.product = None
        self.clear_info_panel()
        if self.ui.tabWidget_main.currentIndex() == 0:
            self.ui.label_header.setText("ИНСТРУМЕНТЫ")
            self.update_table_profiletool()
        elif self.ui.tabWidget_main.currentIndex() == 1:
            self.ui.label_header.setText("ИЗДЕЛИЯ")
            self.update_table_product()

    def update_table_profiletool(self):
        """Обновление таблицы инструментов профиля"""
        BaseTable.populate_table(
            self.ui.tableWidget_profiletool,
            ["Профиль", "Размер", "Описание"],
            api_manager.table['profiletool'],
            func_row_mapper=lambda t: [
                t['profile']['article'],
                t['dimension']['name'],
                t['description']
            ],
            func_id_getter=lambda t: t['id']
        )
        
        

    def update_table_product(self):
        """Обновление таблицы изделий"""
        BaseTable.populate_table(
            self.ui.tableWidget_product,
            ["Название", "Департамент", "Описание"],
            api_manager.table['product'],
            func_row_mapper=lambda p: [
                p['name'],
                p['department']['name'],
                p['description']
            ],
            func_id_getter=lambda p: p['id']
        )

    def update_profiletool_info_panel(self):
        """Обновление панели инструмента профиля"""
        self.update_profiletool_component_table()

    def update_product_info_panel(self):
        """Обновление панели изделия"""
        self.update_product_component_table()

    def update_profiletool_component_table(self):
        """Обновление таблицы компонентов инструмента профиля"""
        
        def map_component_row(component: dict) -> list:
            """Преобразование компонента в строку таблицы"""
            # Название компонента
            name = component["type"]["name"]
            
            # Последний статус из истории
            if component['history']:
                last_history = component['history'][-1]
                status = last_history["status"]["name"]
            else:
                status = "Новая"
            
            # Вариант
            variant = str(component["variant"])
            
            # Описание без переносов строк
            description = component["description"].replace('\n', ' ')
            
            return [name, status, variant, description]
        
        BaseTable.populate_table(
            self.ui.tableWidget_component,
            ["Название", "Статус", "Вариант", "Описание"],
            self.profiletool['component'],
            func_row_mapper=map_component_row,
            func_id_getter=lambda c: c["id"]
        )
        
        # Контекстное меню
        table = self.ui.tableWidget_component
        table.setContextMenuPolicy(Qt.CustomContextMenu)
        table.customContextMenuRequested.connect(self.show_context_menu_component_table)

    def update_product_component_table(self):
        """Обновление таблицы компонентов изделия"""
        BaseTable.populate_table(
            self.ui.tableWidget_component,
            ["Название", "Количество", "Описание"],
            self.product['component'],
            func_row_mapper=lambda c: [
                c["name"],
                str(c["quantity"]),
                c["description"]
            ],
            func_id_getter=lambda c: c["id"]
        )

    def update_table_component_history(self, profiletool_component_id):
        """
        Заполняет tableWidget_component_stage для изделия:
        группировка по задачам (type.name), внутри — этапы
        """
        table = self.ui.tableWidget_component_stage
        
        # Собираем историю
        history_data = []
        for profiletool in api_manager.table['profiletool']:
            for component in profiletool["component"]:
                if component['id'] == profiletool_component_id:
                    for history in component["history"]:
                        history_data.append({
                            "type_name": history['status']['name'],
                            "date": history["date"],
                            "description": history["description"]
                        })

        # Заполняем таблицу
        BaseTable.setup_table(table, ["Тип работы", "Дата", "Описание"], len(history_data))
        
        for row, data in enumerate(history_data):
            BaseTable.set_cell_value(table, row, 0, data["type_name"])
            BaseTable.set_cell_value(table, row, 1, data["date"])
            BaseTable.set_cell_value(table, row, 2, data["description"])


    def clear_info_panel(self):
        """Очистка панели компонентов"""
        BaseTable.clear_table(self.ui.tableWidget_component)
        BaseTable.clear_table(self.ui.tableWidget_component_stage)

    def show_context_menu_component_table(self, pos):
        """Показать контекстное меню для изменения статуса компонента"""
        table = self.ui.tableWidget_component
        menu = QMenu(table)
        status_menu = QMenu("Изменить статус", menu)
        for status in api_manager.directory['component_status']:
            if status['name'] in ['На испытаниях', 'В работе', 'На исправление', 'Брак']:
                action = QAction(status['name'], status_menu)
                action.setCheckable(True)
                action.triggered.connect(lambda _, status_id=status['id']: self.change_component_history(status_id))
                status_menu.addAction(action)
        menu.addMenu(status_menu)
        menu.exec(table.viewport().mapToGlobal(pos))

    # =============================================================================
    # ОБРАБОТЧИКИ СОБЫТИЙ: ВЫДЕЛЕНИЕ
    # =============================================================================
    def on_main_table_clicked(self):
        """Обработчик выбора элемента"""
        if self.ui.tabWidget_main.currentIndex() == 0:
            self.profiletool = api_manager.get_by_id("profiletool", self.ui.tableWidget_profiletool.currentItem().data(Qt.UserRole))
            self.update_profiletool_info_panel()
        elif self.ui.tabWidget_main.currentIndex() == 1:
            self.product = api_manager.get_by_id("product", self.ui.tableWidget_product.currentItem().data(Qt.UserRole))
            self.update_product_info_panel()

    def on_component_clicked(self, item):
        """Обработка выбора компонента"""
        self.component_id = item.data(Qt.UserRole)
        self.update_table_component_history(self.component_id)

    # =============================================================================
    # ОБРАБОТЧИКИ ДОПОЛНИТЕЛЬНЫХ ДЕЙСТВИЙ
    # =============================================================================
    def filter_table(self):
        """Фильтрация строк таблицы"""
        if self.ui.tabWidget_main.currentIndex() == 0:
            table = self.ui.tableWidget_profiletool
            text = self.ui.lineEdit_search_profiletool.text().lower()
        elif self.ui.tabWidget_main.currentIndex() == 1:
            table = self.ui.tableWidget_product
            text = self.ui.lineEdit_search_product.text().lower()

        for row in range(table.rowCount()):
            item = table.item(row, 0)
            if item:
                visible = text.lower() in item.text().lower()
                table.setRowHidden(row, not visible)

    def change_component_history(self, status):
        """Обновление истории компонентов задачи"""
        
        api_manager.api_profiletool.create_profiletool_component_history(
            self.component_id,
            {
                "date": QDate.currentDate().toString("yyyy-MM-dd"),
                "status_id": status,
                "description": ""
            }
        )

        self.update_profiletool_component_table()

    # =============================================================================
    # ОБРАБОТЧИКИ СОБЫТИЙ: УПРАВЛЕНИЕ
    # =============================================================================
    def on_profiletool_add_clicked(self):
        """Добавление инструмента профиля"""
        dialog = DialogCreateProfileTool(self)
        if dialog.exec() == QDialog.Accepted:
            QMessageBox.warning(self, "Внимание", "Инструмент профиля добавлен")

    def on_product_add_clicked(self):
        """Добавление изделия"""
        dialog = DialogCreateProduct(self)
        if dialog.exec() == QDialog.Accepted:
            QMessageBox.warning(self, "Внимание", "Изделие добавлено")

    def on_profiletool_edit_clicked(self):
        """Редактирование инструмента профиля"""
        QMessageBox.warning(self, "Внимание", "Функция будет реализована позже")
        return
        if self.profiletool:
            dialog = DialogEditProfileTool(self.profiletool, self)
            if dialog.exec() == QDialog.Accepted:
                QMessageBox.warning(self, "Внимание", "Инструмент профиля обновлен")
        else:
            QMessageBox.warning(self, "Внимание", "Выберите инструмент профиля для редактирования")

    def on_product_edit_clicked(self):
        """Редактирование изделия"""
        if self.product:
            dialog = DialogEditProduct(self.product, self)
            if dialog.exec() == QDialog.Accepted:
                QMessageBox.warning(self, "Внимание", "Изделие обновлено")
        else:
            QMessageBox.warning(self, "Внимание", "Выберите изделие для редактирования")

    def on_profiletool_delete_clicked(self):
        """Удаление инструмента"""
        if self.profiletool:
            api_manager.api_profiletool.delete_profiletool(self.profiletool['id'])
            QMessageBox.warning(self, "Внимание", "Инструмент профиля удален")
        else:
            QMessageBox.warning(self, "Внимание", "Выберите инструмент профиля для удаления")

    def on_product_delete_clicked(self):
        """Удаление изделия"""
        if self.product:
            api_manager.api_product.delete_product(self.product['id'])
            QMessageBox.warning(self, "Внимание", "Изделие удалено")
        else:
            QMessageBox.warning(self, "Внимание", "Выберите изделие для удаления")

    def on_component_add_clicked(self):
        """Добавление компонента"""
        dialog = DialogCreateProfiletoolComponent(self, self.profiletool)
        if dialog.exec() == QDialog.Accepted:
            QMessageBox.warning(self, "Внимание", "Компонент инструмента профиля добавлен")

    def on_component_delete_clicked(self):
        component_id = self.ui.tableWidget_component.currentItem().data(Qt.UserRole)
        if component_id:
            api_manager.api_profiletool.delete_profiletool_component_by_id(component_id)
            QMessageBox.warning(self, "Внимание", "Компонент удален")
        else:
            QMessageBox.warning(self, "Внимание", "Выберите компонент для удаления")
