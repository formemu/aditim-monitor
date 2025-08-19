"""Диалог для создания инструмента профиля"""
from PySide6.QtWidgets import (QDialog, QTableWidgetItem, 
                               QCheckBox, QAbstractItemView, QListWidgetItem)
from PySide6.QtCore import QFile, Qt, Slot
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QPixmap
import base64

from ..constant import UI_PATHS_ABS as UI_PATHS
from ..api_manager import api_manager


class DialogCreateProfileTool(QDialog):
    """Диалог для создания инструмента профиля с компонентами"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.component_widgets = []   # Список виджетов компонентов (checkbox, combobox)
        self.selected_profile = None

        self.load_ui()
        self.setup_ui()
        
        self.load_dimension()

    def load_ui(self):
        """Загружает UI из файла"""
        ui_file = QFile(UI_PATHS["DIALOG_CREATE_PROFILE_TOOL"])
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
        self.ui.buttonBox.accepted.connect(self.create_profile_tool)
        self.ui.buttonBox.rejected.connect(self.reject)

        # Подключаем поиск профилей
        self.ui.lineEdit_profile_search.textChanged.connect(self.on_profile_search_changed)
        self.ui.listWidget_profile_results.itemClicked.connect(self.on_profile_selected)

        # Настройка таблицы компонентов
        self.ui.tableWidget_components.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ui.tableWidget_components.setSelectionMode(QAbstractItemView.SingleSelection)
        self.ui.tableWidget_components.horizontalHeader().setStretchLastSection(True)
        self.setup_component_form()
        # Устанавливаем ширины колонок
        self.ui.tableWidget_components.setColumnWidth(0, 100)  # Использовать
        self.ui.tableWidget_components.setColumnWidth(1, 200)  # Тип компонента
        self.ui.tableWidget_components.setColumnWidth(2, 150)  # Статус

    # =============================================================================
    # Загрузка справочников и начальных данных
    # =============================================================================
    def load_dimension(self):
        """Загружает размерности по умолчанию"""
        # Загружаем размерности инструментов из справочника
        self.ui.comboBox_dimension.clear()
        for dimension in api_manager.profile_tool_dimension:
            name = dimension['name']
            dimension_id = dimension['id']
            self.ui.comboBox_dimension.addItem(name, dimension_id)

    def setup_component_form(self):
        """Загружает типы компонентов в таблицу"""
        # Очищаем таблицу
        self.ui.tableWidget_components.setRowCount(0)
        self.component_widgets.clear()

        # Заполняем таблицу типами компонентов
        self.ui.tableWidget_components.setRowCount(len(api_manager.component_type))
        for row, type in enumerate(api_manager.component_type):
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
            self.component_widgets.append({
                'type_id': type['id'],
                'checkbox': checkbox,
                'row': row
            })

    # =============================================================================
    # Управление поиском и выбором профиля
    # =============================================================================
    @Slot(str)
    def on_profile_search_changed(self, text: str):
        """Обработчик изменения поискового запроса"""
        self.ui.listWidget_profile_results.clear()
        # Ищем профили через api_manager
        search_results = api_manager.get_search_profile(text)
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
            self.load_profile_sketch(profile['id'])
        else:
            pass

    def load_profile_sketch(self, profile_id: int):
        """Загружает и отображает эскиз профиля"""
        # Получаем данные профиля из references_manager

        profile = api_manager.get_profile_by_id(profile_id)
        if profile and profile['sketch']:

            # Конвертируем base64 в QPixmap
            sketch_data = profile['sketch']
            if sketch_data.startswith('data:image'):
                # Убираем префикс data:image/...;base64,
                base64_data = sketch_data.split(',')[1]
            else:
                base64_data = sketch_data
            image_data = base64.b64decode(base64_data)
            pixmap = QPixmap()
            pixmap.loadFromData(image_data)
            if not pixmap.isNull():
                # Масштабируем изображение под размер label
                scaled_pixmap = pixmap.scaled(
                    200, 150,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                self.ui.label_profile_sketch.setPixmap(scaled_pixmap)
                self.ui.label_profile_sketch.setText("")
            else:
                self.ui.label_profile_sketch.setText("Ошибка загрузки эскиза")
        else:
            self.ui.label_profile_sketch.setText("Эскиз не найден")

    def get_selected_component(self):
        """Возвращает список выбранных компонентов"""
        selected_components = []
        for widget_data in self.component_widgets:
            checkbox = widget_data['checkbox']
            if checkbox.isChecked():
                row = widget_data['row']
                # Получаем описание из таблицы
                description_item = self.ui.tableWidget_components.item(row, 3)
                description = description_item.text() if description_item else ""
                component_data = {
                    "type_id": widget_data['type_id'],
                    "variant": 1,
                    "description": description,
                    "status_id": 1
                }
                selected_components.append(component_data)
        return selected_components

    # =============================================================================
    # Создание инструмента профиля
    # =============================================================================
    @Slot()
    def create_profile_tool(self):
        """Создает новый инструмент профиля"""
        dimension = self.ui.comboBox_dimension.currentData()
        description = self.ui.textEdit_description.toPlainText().strip()

        tool_data = {
            "profile_id": self.selected_profile['id'],
            "dimension_id": dimension,
            "description": description
        }
         # Отправляем запрос на сервер для создания инструмента
        result = api_manager.api_profile_tool.create_profile_tool(tool_data)
        tool_id = result['id']
        if not tool_id:
            raise ValueError("Сервер не вернул ID созданного инструмента")
        # Создаем выбранные компоненты
        for component_data in self.get_selected_component():
            api_manager.api_profile_tool.create_profile_tool_component(tool_id, component_data)

        # Закрываем диалог
        self.accept()
