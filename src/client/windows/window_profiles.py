"""
Содержимое профилей для ADITIM Monitor Client
"""

from PySide6.QtWidgets import QWidget, QMessageBox, QTableWidgetItem
from PySide6.QtCore import QFile
from PySide6.QtUiTools import QUiLoader

from ..constants import UI_PATHS_ABS as UI_PATHS
from ..widgets.dialog_create_profile import DialogCreateProfile
from ..api_client import ApiClient


class ProfilesContent(QWidget):
    """Виджет содержимого профилей"""
    
    def __init__(self, api_client: ApiClient = None):
        super().__init__()
        self.api_client = api_client or ApiClient()
        self.load_ui()
        self.setup_ui()
        self.load_profiles_from_server()

    def load_ui(self):
        """Загрузка UI из файла"""
        ui_file = QFile(UI_PATHS["PROFILES_CONTENT"])
        ui_file.open(QFile.ReadOnly)
        
        loader = QUiLoader()
        self.ui = loader.load(ui_file)
        ui_file.close()

    def setup_ui(self):
        """Настройка UI компонентов после загрузки"""
        self.ui.pushButton_profile_add.clicked.connect(self.on_add_clicked)
        self.ui.pushButton_profile_edit.clicked.connect(self.on_edit_clicked)
        self.ui.pushButton_profile_delete.clicked.connect(self.on_delete_clicked)
        self.ui.pushButton_sketch_open.clicked.connect(self.on_sketch_open_clicked)
        self.ui.pushButton_autocad_open.clicked.connect(self.on_autocad_open_clicked)
        self.ui.tableWidget_profiles.itemSelectionChanged.connect(self.on_selection_changed)
        self.ui.lineEdit_search.textChanged.connect(self.on_search_changed)
        
        # Настройка ширины колонок
        self.ui.tableWidget_profiles.setColumnWidth(0, 150)  # Артикул - фиксированная ширина
        self.ui.tableWidget_profiles.horizontalHeader().setStretchLastSection(True)  # Описание - растягивается

    def on_add_clicked(self):
        """Добавление нового профиля"""
        try:
            # Создаем диалог создания профиля
            dialog = DialogCreateProfile(self.api_client, self)
            
            # Подключаем сигнал успешного создания профиля
            dialog.profile_created.connect(self.on_profile_created)
            
            # Показываем диалог
            dialog.exec()
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось открыть диалог создания профиля: {e}")

    def on_profile_created(self, profile_data):
        """Обработчик успешного создания профиля"""
        try:
            # Перезагружаем список профилей с сервера
            self.load_profiles_from_server()
            
            # Находим и выделяем новый профиль в таблице
            for row in range(self.ui.tableWidget_profiles.rowCount()):
                article_item = self.ui.tableWidget_profiles.item(row, 0)
                if article_item and article_item.text() == profile_data.get('article', ''):
                    self.ui.tableWidget_profiles.selectRow(row)
                    break
                    
        except Exception as e:
            QMessageBox.warning(self, "Предупреждение", f"Профиль создан, но не удалось обновить список: {e}")

    def load_profiles_from_server(self):
        """Загружает профили с сервера"""
        try:
            profiles = self.api_client.get_profiles()
            
            # Очищаем таблицу
            self.ui.tableWidget_profiles.setRowCount(0)
            
            # Заполняем таблицу данными с сервера
            self.ui.tableWidget_profiles.setRowCount(len(profiles))
            
            for row, profile in enumerate(profiles):
                # Артикул
                article_item = QTableWidgetItem(profile.get('article', ''))
                self.ui.tableWidget_profiles.setItem(row, 0, article_item)
                
                # Описание
                description_item = QTableWidgetItem(profile.get('description', ''))
                self.ui.tableWidget_profiles.setItem(row, 1, description_item)
                
        except Exception as e:
            QMessageBox.warning(self, "Предупреждение", f"Не удалось загрузить профили с сервера: {e}")
            # Загружаем тестовые данные в случае ошибки
            self.load_sample_data()

    def load_sample_data(self):
        """Загружает тестовые данные (fallback)"""
        sample_profiles = [
            ("ПР-001-2024", "Стандартный оконный профиль"),
            ("ПР-002-2024", "Усиленный профиль для промышленных объектов"), 
            ("ПР-003-2024", "Энергосберегающий профиль"),
            ("ПР-004-2024", "Декоративный профиль"),
            ("ПР-005-2024", "Угловой профиль")
        ]
        
        self.ui.tableWidget_profiles.setRowCount(len(sample_profiles))
        
        for row, (article, description) in enumerate(sample_profiles):
            # Артикул
            article_item = QTableWidgetItem(article)
            self.ui.tableWidget_profiles.setItem(row, 0, article_item)
            
            # Описание
            description_item = QTableWidgetItem(description)
            self.ui.tableWidget_profiles.setItem(row, 1, description_item)

    def on_edit_clicked(self):
        """Редактирование профиля"""
        QMessageBox.information(self, "Редактировать", "Редактирование профиля")

    def on_delete_clicked(self):
        """Удаление профиля"""
        QMessageBox.information(self, "Удалить", "Удаление профиля")

    def on_sketch_open_clicked(self):
        """Открытие эскиза"""
        QMessageBox.information(self, "Эскиз", "Открытие эскиза")

    def on_autocad_open_clicked(self):
        """Открытие чертежа в AutoCAD"""
        QMessageBox.information(self, "AutoCAD", "Открытие в AutoCAD")

    def on_selection_changed(self):
        """Изменение выбранного профиля"""
        selected_items = self.ui.tableWidget_profiles.selectedItems()
        if selected_items:
            self.ui.pushButton_sketch_open.setEnabled(True)
            self.ui.pushButton_autocad_open.setEnabled(True)
            # Обновляем информацию в панели предварительного просмотра
            row = selected_items[0].row()
            article = self.ui.tableWidget_profiles.item(row, 0).text()
            description = self.ui.tableWidget_profiles.item(row, 1).text() if self.ui.tableWidget_profiles.item(row, 1) else ""
            self.ui.label_profile_article.setText(f"Артикул: {article}")
            self.ui.label_profile_name.setText(f"Описание: {description}")
        else:
            self.ui.pushButton_sketch_open.setEnabled(False)
            self.ui.pushButton_autocad_open.setEnabled(False)
            self.ui.label_profile_article.setText("Артикул: -")
            self.ui.label_profile_name.setText("Описание: -")

    def on_search_changed(self, text):
        """Поиск по артикулу"""
        # Простая фильтрация по артикулу
        for row in range(self.ui.tableWidget_profiles.rowCount()):
            item = self.ui.tableWidget_profiles.item(row, 0)
            if item:
                visible = text.lower() in item.text().lower()
                self.ui.tableWidget_profiles.setRowHidden(row, not visible)
