"""Содержимое изделий для ADITIM Monitor Client с вкладками и компонентами"""
from ast import Pass
from PySide6.QtWidgets import QWidget, QMessageBox, QTableWidgetItem,  QTableWidgetItem, QDialog
from PySide6.QtCore import QFile, Qt
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QPixmap
from ..constant import UI_PATHS_ABS, ICON_PATHS_ABS, get_style_path
from ..style_util import load_styles
from ..api_manager import api_manager
from ..widgets.profiletool.dialog_create_profiletool import DialogCreateProfileTool
from ..widgets.profiletool.dialog_edit_profiletool import DialogEditProfileTool
from ..widgets.product.dialog_create_product import DialogCreateProduct
from ..widgets.product.dialog_edit_product import DialogEditProduct

class WindowProduct(QWidget):
    """Виджет содержимого изделий с вкладками"""
    def __init__(self):
        super().__init__()
        self.profiletool = None
        self.product = None
        self.load_ui()
        self.setup_ui()
        api_manager.data_updated.connect(self.refresh_data)

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
        self.load_logo()
        # Общие подключения
        self.ui.tabWidget_main.currentChanged.connect(self.refresh_data)
        # Подключения: профили
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
        self.ui.pushButton_component_edit.clicked.connect(self.on_component_edit_clicked)
        self.ui.pushButton_component_delete.clicked.connect(self.on_component_delete_clicked)
        self.ui.tableWidget_component.itemClicked.connect(self.on_component_clicked)

        # Инициализация таблицы
        self.refresh_data()

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
        """Обновление таблицы инструментов профиля с корректным отображением и заполнением по ширине"""
        table = self.ui.tableWidget_profiletool
        table.setRowCount(len(api_manager.table['profiletool']))
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["Профиль", "Размер ","Описание"])

        for row, tool in enumerate(api_manager.table['profiletool']):
            item_name = QTableWidgetItem(tool['profile']['article'])
            item_dimension = QTableWidgetItem(tool['dimension']['name'])
            item_description = QTableWidgetItem(tool['description'])

            item_name.setData(Qt.UserRole, tool['id'])
            item_dimension.setData(Qt.UserRole, tool['id'])
            item_description.setData(Qt.UserRole, tool['id'])

            table.setItem(row, 0, item_name)
            table.setItem(row, 1, item_dimension)
            table.setItem(row, 2, item_description)

    def update_table_product(self):
        """Обновление таблицы изделий с корректным отображением и заполнением по ширине"""
        table = self.ui.tableWidget_product
        table.setRowCount(len(api_manager.table['product']))
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["Название", "Департамент", "Описание"])

        for row, product in enumerate(api_manager.table['product']):
            item_name = QTableWidgetItem(product['name'])
            item_department = QTableWidgetItem(product['department']['name'])
            item_description = QTableWidgetItem(product['description'])

            item_name.setData(Qt.UserRole, product['id'])
            item_department.setData(Qt.UserRole, product['id'])
            item_description.setData(Qt.UserRole, product['id'])

            table.setItem(row, 0, item_name)
            table.setItem(row, 1, item_department)
            table.setItem(row, 2, item_description)

    def update_profiletool_info_panel(self):
        """Обновление панели инструмента профиля"""
        self.update_profiletool_component_table()

    def update_product_info_panel(self):
        """Обновление панели изделия"""
        self.update_product_component_table()

    def update_profiletool_component_table(self):
        """Обновление таблицы компонентов инструмента профиля"""
        self.ui.tableWidget_component.setRowCount(0)
        self.ui.tableWidget_component.setColumnCount(2)
        self.ui.tableWidget_component.setHorizontalHeaderLabels(["Название", "Статус"])
        self.ui.tableWidget_component.setRowCount(len(self.profiletool['component']))

        for row, component in enumerate(self.profiletool['component']):
            name_item = QTableWidgetItem(component["type"]["name"])
            status_item = QTableWidgetItem(component["status"]["name"])
            
            name_item.setData(Qt.UserRole, component["id"])
            status_item.setData(Qt.UserRole, component["id"])

            self.ui.tableWidget_component.setItem(row, 0, name_item)
            self.ui.tableWidget_component.setItem(row, 1, status_item)

    def update_product_component_table(self):
        """Обновление таблицы компонентов изделия"""
        self.ui.tableWidget_component.setRowCount(0)
        self.ui.tableWidget_component.setColumnCount(2)
        self.ui.tableWidget_component.setRowCount(len(self.product['component']))
        self.ui.tableWidget_component.setHorizontalHeaderLabels(["Название", "Количество"])

        for row, component in enumerate(self.product['component']):
            name_item = QTableWidgetItem(component["name"])
            quantity_item = QTableWidgetItem(str(component["quantity"]))

            name_item.setData(Qt.UserRole, component["id"])
            quantity_item.setData(Qt.UserRole, component["id"])

            self.ui.tableWidget_component.setItem(row, 0, name_item)
            self.ui.tableWidget_component.setItem(row, 1, quantity_item)

    def update_table_component_stage(self, profiletool_component_id):
        """
        Заполняет tableWidget_component_stage для изделия:
        группировка по задачам (type.name), внутри — этапы
        """
        self.ui.tableWidget_component_stage.setColumnCount(3)
        self.ui.tableWidget_component_stage.setHorizontalHeaderLabels(["Тип работы", "Начата" , "Завершена"])
        stage_data = []
        for task in api_manager.table['task']:
            for component in task["component"]:
                if component['profiletool_component_id'] == profiletool_component_id:
                    stage_data.append({
                        "create" : task["created"],
                        "completed" : task["completed"],
                        "task_type": task["type"]["name"],
                    })

        self.ui.tableWidget_component_stage.setRowCount(len(stage_data))

        for row, data in enumerate(stage_data):
                self.ui.tableWidget_component_stage.setItem(row, 0, QTableWidgetItem(data["task_type"]))
                self.ui.tableWidget_component_stage.setItem(row, 1, QTableWidgetItem(data["create"]))
                self.ui.tableWidget_component_stage.setItem(row, 2, QTableWidgetItem(data["completed"]))

    def clear_info_panel(self):
        """Очистка панели компонентов"""
        self.ui.tableWidget_component.setRowCount(0)
        self.ui.tableWidget_component_stage.setRowCount(0)

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

    def on_component_clicked(self):
        """Обработка выбора компонента"""
        self.update_table_component_stage(self.ui.tableWidget_component.currentItem().data(Qt.UserRole))

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
            item = table.item(row, 1)
            if item:
                visible = text.lower() in item.text().lower()
                table.setRowHidden(row, not visible)

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
        QMessageBox.information(self, "Информация", "Функция будет реализована позже")

    def on_component_edit_clicked(self):
        """Редактирование компонента"""
        QMessageBox.information(self, "Информация", "Функция будет реализована позже")

    def on_component_delete_clicked(self):
        """Удаление компонента"""
        QMessageBox.information(self, "Информация", "Функция будет реализована позже")

