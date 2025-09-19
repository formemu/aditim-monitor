"""Диалог для создания инструмента профиля"""
from PySide6.QtWidgets import (QDialog, QTableWidgetItem, QCheckBox, QAbstractItemView, QListWidgetItem)
from PySide6.QtCore import QFile, Qt, Slot
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QPixmap
import base64
from ...constant import UI_PATHS_ABS
from ...api_manager import api_manager

class DialogCreateProfileTool(QDialog):
    """Диалог для создания инструмента профиля с компонентами"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.list_component_widget = []
        self.selected_profile = None
        self.load_ui()
        self.load_dimension()
        self.setup_ui()
        self.setup_component_table()

    def load_ui(self):
        """Загружает UI из файла"""
        ui_file = QFile(UI_PATHS_ABS["DIALOG_CREATE_PROFILE_TOOL"])
        ui_file.open(QFile.ReadOnly)
        loader = QUiLoader()
        self.ui = loader.load(ui_file)
        ui_file.close()
        # Устанавливаем заголовок и свойства диалога
        self.setWindowTitle("Создание инструмента профиля")
        self.setModal(True)
        self.setLayout(self.ui.layout())
        
    def setup_ui(self):
        """Настраивает UI компонентов после загрузки"""
        # Подключаем обработчики кнопок
        self.ui.buttonBox.accepted.connect(self.accept)
        self.ui.buttonBox.rejected.connect(self.reject)
        # Подключаем поиск профилей
        self.ui.lineEdit_profile_search.textChanged.connect(self.on_profile_search_changed)
        self.ui.listWidget_profile_results.itemClicked.connect(self.on_profile_selected)
        # Настройка таблицы компонентов
        self.ui.tableWidget_components.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ui.tableWidget_components.setSelectionMode(QAbstractItemView.SingleSelection)
        self.ui.tableWidget_components.horizontalHeader().setStretchLastSection(True)

        # Устанавливаем ширины колонок
        self.ui.tableWidget_components.setColumnWidth(0, 100)  # Использовать
        self.ui.tableWidget_components.setColumnWidth(1, 200)  # Тип компонента
        self.ui.tableWidget_components.setColumnWidth(2, 150)  # Статус

    # =============================================================================
    # Загрузка справочников и начальных данных
    # =============================================================================
    def load_dimension(self):
        """Загружает размерности по умолчанию"""
        self.ui.comboBox_dimension.clear()
        for dimension in api_manager.directory['profile_tool_dimension']:
            name = dimension['name']
            dimension_id = dimension['id']
            self.ui.comboBox_dimension.addItem(name, dimension_id)

    # =============================================================================
    # Управление таблицей компонентов
    # =============================================================================
    def setup_component_table(self):
        """Загружает типы компонентов в таблицу"""
        # Очищаем таблицу
        self.ui.tableWidget_components.setRowCount(0)
        self.list_component_widget.clear()

        # Заполняем таблицу типами компонентов
        self.ui.tableWidget_components.setRowCount(len(api_manager.directory['component_type']))
        for row, type in enumerate(api_manager.directory['component_type']):
            # Колонка 0: Checkbox "Использовать"
            checkbox = QCheckBox()
            checkbox.setChecked(False)  # По умолчанию не выбран
            self.ui.tableWidget_components.setCellWidget(row, 0, checkbox)
            # Колонка 1: Название типа компонента
            name_item = QTableWidgetItem(type['name'])
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
            name_item.setData(Qt.UserRole, type['id'])
            self.ui.tableWidget_components.setItem(row, 1, name_item)
            # Сохраняем ссылки на виджеты для удобного доступа
            self.list_component_widget.append({
                'type_id': type['id'],
                'checkbox': checkbox,
                'row': row
            })

    # =============================================================================
    # Управление поиском и выбором профиля
    # =============================================================================
    @Slot(str)
    def on_profile_search_changed(self, text):
        """Обработчик изменения поискового запроса"""
        self.ui.listWidget_profile_results.clear()
        # Ищем профили через api_manager
        search_results = api_manager.search_in('profile', 'article', text)
        for profile in search_results[:10]:  # Показываем максимум 10 результатов
            display_text = f"{profile['article']} - {profile.get('description', '')}"
            item = QListWidgetItem(display_text)
            # Сохраняем данные профиля в элементе списка
            item.setData(Qt.UserRole, profile)
            self.ui.listWidget_profile_results.addItem(item)

    @Slot(QListWidgetItem)
    def on_profile_selected(self, item):
        """Обработчик выбора профиля из списка"""
        profile = item.data(Qt.UserRole)
        if profile:
            self.selected_profile = profile
            # Обновляем поле поиска
            self.ui.lineEdit_profile_search.setText(profile['article'])
            # Скрываем список результатов
            self.ui.listWidget_profile_results.clear()
            # Загружаем эскиз профиля
            self.load_profile_sketch(profile)
        else:
            pass

    def load_profile_sketch(self, profile):
        """Загружает и отображает эскиз профиля"""
        # Получаем данные профиля из api_manager
        if profile and profile['sketch']:
            # Конвертируем base64 в QPixmap
            sketch_data = profile['sketch']
            if sketch_data.startswith('data:image'):
                # Убираем префикс data:image/...;base64,
                base64_data = sketch_data.split(',')[1]
            else:
                base64_data = sketch_data
            # Декодируем base64 и создаем QPixmap
            image_data = base64.b64decode(base64_data)
            pixmap = QPixmap()
            if pixmap.loadFromData(image_data):
                # Масштабируем изображение
                scaled_pixmap = pixmap.scaled(200, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.ui.label_profile_sketch.setPixmap(scaled_pixmap)
                self.ui.label_profile_sketch.setText("")
                return
        # Если эскиз не найден, показываем заглушку
        self.ui.label_profile_sketch.clear()
        self.ui.label_profile_sketch.setText("Эскиз не найден")

    def get_selected_component(self):
        """Возвращает список выбранных компонентов"""
        list_selected_component = []
        for widget_data in self.list_component_widget:
            checkbox = widget_data['checkbox']
            if checkbox.isChecked():
                row = widget_data['row']
                # Получаем описание из таблицы
                description_item = self.ui.tableWidget_components.item(row, 3)
                description = description_item.text() if description_item else ""
                component = {
                    "type_id": widget_data['type_id'],
                    "variant": 1,
                    "description": description,
                    "status_id": 1
                }
                list_selected_component.append(component)
        return list_selected_component

    # =============================================================================
    # Создание инструмента профиля
    # =============================================================================
    @Slot()
    def create_profile_tool(self):
        """Создает новый инструмент профиля"""
        dimension = self.ui.comboBox_dimension.currentData()
        description = self.ui.textEdit_description.toPlainText().strip()
        tool = {
            "profile_id": self.selected_profile['id'],
            "dimension_id": dimension,
            "description": description
        }
         # Создаем инструмент
        result = api_manager.api_profile_tool.create_profile_tool(tool)
        profile_tool_id = result['id']
        # Создаем выбранные компоненты
        for component in self.get_selected_component():
            api_manager.api_profile_tool.create_profile_tool_component(profile_tool_id, component)

    def accept(self):
        """Принимает изменения и закрывает диалог"""
        self.create_profile_tool()
        super().accept()