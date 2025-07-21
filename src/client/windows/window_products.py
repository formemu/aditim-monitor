"""
Содержимое изделий для ADITIM Monitor Client
"""

from PySide6.QtWidgets import QWidget, QMessageBox, QTableWidgetItem, QAbstractItemView
from PySide6.QtCore import QFile, Qt, QTimer
from PySide6.QtUiTools import QUiLoader

from ..constants import UI_PATHS_ABS as UI_PATHS, get_style_path
from ..api_client import ApiClient
from ..style_utils import load_styles_with_constants
from ..async_utils import run_async


class ProductsContent(QWidget):
    """Виджет содержимого изделий"""
    
    def __init__(self, api_client: ApiClient = None):
        super().__init__()
        self.api_client = api_client or ApiClient()
        self.departments = {}  # Словарь для кеширования департаментов
        self.load_ui()
        self.setup_ui()
        self.load_departments()
        self.load_products_from_server()

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
        
        # Подключение кнопок
        self.ui.pushButton_product_add.clicked.connect(self.on_add_clicked)
        self.ui.pushButton_product_edit.clicked.connect(self.on_edit_clicked)
        self.ui.pushButton_product_delete.clicked.connect(self.on_delete_clicked)
        self.ui.pushButton_view_details.clicked.connect(self.on_view_details_clicked)
        self.ui.pushButton_create_task.clicked.connect(self.on_create_task_clicked)
        self.ui.tableWidget_products.itemSelectionChanged.connect(self.on_selection_changed)
        self.ui.lineEdit_search.textChanged.connect(self.on_search_changed)
        
        # Настройка режима выделения таблицы
        self.ui.tableWidget_products.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ui.tableWidget_products.setSelectionMode(QAbstractItemView.SingleSelection)
        self.ui.tableWidget_products.setFocusPolicy(Qt.NoFocus)
        
        # Настройка ширины колонок
        self.ui.tableWidget_products.setColumnWidth(0, 180)  # Название
        self.ui.tableWidget_products.setColumnWidth(1, 120)  # Артикул  
        self.ui.tableWidget_products.setColumnWidth(2, 150)  # Департамент
        self.ui.tableWidget_products.horizontalHeader().setStretchLastSection(True)  # Описание - растягивается
        
        # Настройка автоматического обновления каждые 5 секунд
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.load_products_async)
        self.update_timer.start(5000)  # 5000 мс = 5 секунд

    def load_departments(self):
        """Загружает справочник департаментов"""
        try:
            departments = self.api_client.get_departments()
            self.departments = {dept['id']: dept['name'] for dept in departments}
        except Exception as e:
            print(f"Ошибка загрузки департаментов: {e}")
            self.departments = {}

    def load_products_from_server(self):
        """Загружает изделия с сервера"""
        try:
            products = self.api_client.get_products()
            
            # Очищаем таблицу
            self.ui.tableWidget_products.setRowCount(0)
            
            # Заполняем таблицу данными с сервера
            self.ui.tableWidget_products.setRowCount(len(products))
            
            for row, product in enumerate(products):
                # Название
                name_item = QTableWidgetItem(product.get('name', ''))
                name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
                self.ui.tableWidget_products.setItem(row, 0, name_item)
                
                # Артикул
                article_item = QTableWidgetItem(product.get('article', ''))
                article_item.setFlags(article_item.flags() & ~Qt.ItemIsEditable)
                self.ui.tableWidget_products.setItem(row, 1, article_item)
                
                # Департамент
                dept_id = product.get('id_departament', 0)
                dept_name = self.departments.get(dept_id, f"ID: {dept_id}")
                dept_item = QTableWidgetItem(dept_name)
                dept_item.setFlags(dept_item.flags() & ~Qt.ItemIsEditable)
                self.ui.tableWidget_products.setItem(row, 2, dept_item)
                
                # Описание
                description_item = QTableWidgetItem(product.get('description', ''))
                description_item.setFlags(description_item.flags() & ~Qt.ItemIsEditable)
                self.ui.tableWidget_products.setItem(row, 3, description_item)
            
            # Убираем текущий активный элемент
            self.ui.tableWidget_products.setCurrentItem(None)
                
        except Exception as e:
            QMessageBox.warning(self, "Предупреждение", f"Не удалось загрузить изделия с сервера: {e}")

    def load_products_async(self):
        """Асинхронная загрузка изделий с сервера"""
        run_async(
            self.api_client.get_products,
            on_success=self.on_products_loaded,
            on_error=self.on_products_load_error
        )

    def on_products_loaded(self, products):
        """Обработчик успешной загрузки изделий"""
        try:
            # Очищаем таблицу
            self.ui.tableWidget_products.setRowCount(0)
            
            # Заполняем таблицу данными с сервера
            self.ui.tableWidget_products.setRowCount(len(products))
            
            for row, product in enumerate(products):
                # Название
                name_item = QTableWidgetItem(product.get('name', ''))
                name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
                self.ui.tableWidget_products.setItem(row, 0, name_item)
                
                # Артикул
                article_item = QTableWidgetItem(product.get('article', ''))
                article_item.setFlags(article_item.flags() & ~Qt.ItemIsEditable)
                self.ui.tableWidget_products.setItem(row, 1, article_item)
                
                # Департамент
                dept_id = product.get('id_departament', 0)
                dept_name = self.departments.get(dept_id, f"ID: {dept_id}")
                dept_item = QTableWidgetItem(dept_name)
                dept_item.setFlags(dept_item.flags() & ~Qt.ItemIsEditable)
                self.ui.tableWidget_products.setItem(row, 2, dept_item)
                
                # Описание
                description_item = QTableWidgetItem(product.get('description', ''))
                description_item.setFlags(description_item.flags() & ~Qt.ItemIsEditable)
                self.ui.tableWidget_products.setItem(row, 3, description_item)
            
            # Убираем текущий активный элемент
            self.ui.tableWidget_products.setCurrentItem(None)
                
        except Exception as e:
            print(f"Ошибка обновления UI изделий: {e}")

    def on_products_load_error(self, error):
        """Обработчик ошибки загрузки изделий"""
        print(f"Ошибка загрузки изделий: {error}")

    def on_add_clicked(self):
        """Добавление нового изделия"""
        QMessageBox.information(self, "Добавить", "Создание нового изделия")

    def on_edit_clicked(self):
        """Редактирование изделия"""
        QMessageBox.information(self, "Редактировать", "Редактирование изделия")

    def on_delete_clicked(self):
        """Удаление изделия"""
        QMessageBox.information(self, "Удалить", "Удаление изделия")

    def on_view_details_clicked(self):
        """Просмотр подробностей изделия"""
        QMessageBox.information(self, "Подробности", "Просмотр подробной информации об изделии")

    def on_create_task_clicked(self):
        """Создание задачи для изделия"""
        QMessageBox.information(self, "Создать задачу", "Создание новой задачи для изделия")

    def on_selection_changed(self):
        """Изменение выбранного изделия"""
        selected_items = self.ui.tableWidget_products.selectedItems()
        if selected_items:
            self.ui.pushButton_view_details.setEnabled(True)
            self.ui.pushButton_create_task.setEnabled(True)
            
            # Обновляем информацию в панели предварительного просмотра
            row = selected_items[0].row()
            name = self.ui.tableWidget_products.item(row, 0).text() if self.ui.tableWidget_products.item(row, 0) else ""
            article = self.ui.tableWidget_products.item(row, 1).text() if self.ui.tableWidget_products.item(row, 1) else ""
            department = self.ui.tableWidget_products.item(row, 2).text() if self.ui.tableWidget_products.item(row, 2) else ""
            description = self.ui.tableWidget_products.item(row, 3).text() if self.ui.tableWidget_products.item(row, 3) else ""
            
            self.ui.label_product_name.setText(f"Название: {name}")
            self.ui.label_product_article.setText(f"Артикул: {article}")
            self.ui.label_product_description.setText(f"Описание: {description}")
        else:
            self.ui.pushButton_view_details.setEnabled(False)
            self.ui.pushButton_create_task.setEnabled(False)
            self.ui.label_product_name.setText("Название: -")
            self.ui.label_product_article.setText("Артикул: -")
            self.ui.label_product_description.setText("Описание: -")

    def on_search_changed(self, text):
        """Поиск по названию изделия"""
        # Простая фильтрация по названию
        for row in range(self.ui.tableWidget_products.rowCount()):
            item = self.ui.tableWidget_products.item(row, 0)  # Название в первой колонке
            if item:
                visible = text.lower() in item.text().lower()
                self.ui.tableWidget_products.setRowHidden(row, not visible)
