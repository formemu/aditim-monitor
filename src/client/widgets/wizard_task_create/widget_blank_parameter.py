"""Виджет параметров заготовки для компонента"""
from PySide6.QtWidgets import QWidget, QCheckBox
from PySide6.QtCore import QFile
from PySide6.QtUiTools import QUiLoader
from ...constant import UI_PATHS_ABS
from ...api_manager import api_manager


class WidgetBlankParameter(QWidget):
    """Виджет для выбора заготовки и указания размеров обработанной детали"""
    
    # ID работ для заготовок
    WORK_EROSION_ID = 8  # Эрозионные работы
    WORK_MILLING_ID = 9  # Фрезерные работы
    EROSION_OFFSET = 0.7  # Припуск для эрозионных работ (мм)
    
    def __init__(self, component, parent=None):
        super().__init__(parent)
        self.component = component
        self.selected_blank = None
        self.load_ui()
        self.setup_ui()
    
    def load_ui(self):
        """Загрузка UI из файла"""
        ui_file = QFile(UI_PATHS_ABS["WIDGET_TASK_CREATE_BLANK"])
        ui_file.open(QFile.ReadOnly)
        loader = QUiLoader()
        self.ui = loader.load(ui_file, self)
        ui_file.close()
        
        # Устанавливаем layout из загруженного UI
        if self.ui.layout():
            self.setLayout(self.ui.layout())
    
    def setup_ui(self):
        """Настройка UI виджета"""
        # Устанавливаем название компонента в GroupBox
        self.ui.groupBox_component.setTitle(f"Компонент: {self.component['type']['name']}")
        
        # Подключаем сигналы
        self.ui.comboBox_material.currentIndexChanged.connect(self.on_material_changed)
        self.ui.comboBox_blank.currentIndexChanged.connect(self.on_blank_selected)
        
        # Отключаем поля размеров детали по умолчанию
        self.ui.spinBox_product_width.setEnabled(False)
        self.ui.spinBox_product_height.setEnabled(False)
        self.ui.spinBox_product_length.setEnabled(False)
        
        # Настройка поля припуска для эрозионных работ
        if hasattr(self.ui, 'doubleSpinBox_erosion_offset'):
            self.ui.doubleSpinBox_erosion_offset.setValue(self.EROSION_OFFSET)
            self.ui.doubleSpinBox_erosion_offset.setSingleStep(0.1)
            self.ui.doubleSpinBox_erosion_offset.setDecimals(1)
        
        # Загружаем работы для заготовок
        self.load_blank_work()
        
        # Загружаем материалы
        self.load_material()
    
    def load_material(self):
        """Загрузка списка материалов"""
        self.ui.comboBox_material.clear()
        self.ui.comboBox_material.addItem("Выберите материал", None)
        for material in api_manager.directory.get('blank_material', []):
            self.ui.comboBox_material.addItem(material['name'], material['id'])
    
    def load_blank_work(self):
        """Загрузка чекбоксов работ для заготовок"""
        # Получаем работы для заготовок из справочника
        list_work = []
        for work in api_manager.directory.get('work_subtype', []):
            if work['id'] in [self.WORK_EROSION_ID, self.WORK_MILLING_ID]:
                list_work.append(work)
        
        # Создаем чекбоксы для каждой работы
        layout = self.ui.widget_work_container.layout()
        for work in list_work:
            checkbox = QCheckBox(work['name'])
            checkbox.setProperty("work_subtype_id", work['id'])
            checkbox.setProperty("work_data", work)  # Сохраняем данные работы
            layout.addWidget(checkbox)
            
            # По умолчанию отмечаем все работы для заготовок
            checkbox.setChecked(True)
    
    def on_material_changed(self):
        """Обработка изменения материала - загрузка доступных размеров заготовок"""
        self.ui.comboBox_blank.clear()
        self.selected_blank = None
        self.clear_blank_info()
        
        material_id = self.ui.comboBox_material.currentData()
        if not material_id:
            return
        
        # Получаем все заготовки
        list_blank = api_manager.table.get('blank', [])
        
        # Фильтруем только прибывшие и не обработанные заготовки
        list_available_blank = [
            blank for blank in list_blank
            if blank.get('material') and blank.get('material')['id'] == material_id
            and blank.get('date_arrival')  # Прибыла
            and not blank.get('date_product')  # Не обработана
            and not blank.get('profiletool_component_id')  # Не привязана к компоненту
        ]
        
        # Группируем по размерам и считаем количество
        dict_size_count = {}
        for blank in list_available_blank:
            width = blank.get('blank_width') or 0
            height = blank.get('blank_height') or 0
            length = blank.get('blank_length') or 0
            size_key = f"{width}×{height}×{length}"
            
            if size_key not in dict_size_count:
                dict_size_count[size_key] = {
                    'width': width,
                    'height': height,
                    'length': length,
                    'count': 0,
                    'list_blank': []
                }
            dict_size_count[size_key]['count'] += 1
            dict_size_count[size_key]['list_blank'].append(blank)
        
        self.ui.comboBox_blank.addItem("Выберите размер", None)
        for size_key, size_data in sorted(dict_size_count.items()):
            text = f"{size_key} мм | Доступно: {size_data['count']} шт"
            self.ui.comboBox_blank.addItem(text, size_data)
    
    def on_blank_selected(self):
        """Обработка выбора размера заготовок"""
        size_data = self.ui.comboBox_blank.currentData()
        
        if not size_data:
            self.selected_blank = None
            self.clear_blank_info()
            return
        
        # Сохраняем данные о размере и списке доступных заготовок
        self.selected_blank = size_data
        
        # Отображаем размеры заготовки
        blank_width = size_data['width']
        blank_height = size_data['height']
        blank_length = size_data['length']
        blank_count = size_data['count']
        
        self.ui.label_blank_width.setText(str(blank_width))
        self.ui.label_blank_height.setText(str(blank_height))
        self.ui.label_blank_length.setText(str(blank_length))
        
        # Предупреждение, если заготовок мало (1 штука)
        if blank_count == 1:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(
                self,
                "Внимание",
                f"Доступна только 1 заготовка размера {blank_width}×{blank_height}×{blank_length} мм.\n"
                f"Если для других компонентов нужен такой же размер, заготовок не хватит!"
            )
        
        # Обновляем размеры детали с учётом работ
        self.update_product_size()
    
    def update_product_size(self):
        """Обновление размеров детали с учётом выбранных работ"""
        if not self.selected_blank:
            return
        
        blank_width = self.selected_blank['width']
        blank_height = self.selected_blank['height']
        blank_length = self.selected_blank['length']
        
        # Получаем размеры из типа компонента
        component_type = self.component.get('type', {})
        type_width = component_type.get('width') or blank_width
        type_height = component_type.get('height') or blank_height
        type_length = component_type.get('length') or blank_length
        
        # Используем размеры типа компонента (без припуска)
        # Припуск будет указан в описании этапа эрозионных работ
        product_width = min(type_width, blank_width) if blank_width > 0 else type_width
        product_height = min(type_height, blank_height) if blank_height > 0 else type_height
        product_length = min(type_length, blank_length) if blank_length > 0 else type_length
        
        # Активируем поля размеров детали и устанавливаем максимумы
        self.ui.spinBox_product_width.setEnabled(True)
        self.ui.spinBox_product_width.setMaximum(blank_width if blank_width > 0 else 9999)
        self.ui.spinBox_product_width.setValue(int(product_width) if product_width > 0 else 0)
        
        self.ui.spinBox_product_height.setEnabled(True)
        self.ui.spinBox_product_height.setMaximum(blank_height if blank_height > 0 else 9999)
        self.ui.spinBox_product_height.setValue(int(product_height) if product_height > 0 else 0)
        
        self.ui.spinBox_product_length.setEnabled(True)
        self.ui.spinBox_product_length.setMaximum(blank_length if blank_length > 0 else 9999)
        self.ui.spinBox_product_length.setValue(int(product_length) if product_length > 0 else 0)
    
    def is_work_checked(self, work_id):
        """Проверяет, отмечен ли чекбокс работы"""
        layout = self.ui.widget_work_container.layout()
        for i in range(layout.count()):
            widget = layout.itemAt(i).widget()
            if isinstance(widget, QCheckBox):
                if widget.property("work_subtype_id") == work_id:
                    return widget.isChecked()
        return False
    
    def get_selected_work(self):
        """Получает список отмеченных работ"""
        list_selected_work = []
        layout = self.ui.widget_work_container.layout()
        for i in range(layout.count()):
            widget = layout.itemAt(i).widget()
            if isinstance(widget, QCheckBox) and widget.isChecked():
                work_data = widget.property("work_data")
                if work_data:
                    list_selected_work.append(work_data)
        return list_selected_work
    
    def clear_blank_info(self):
        """Очистка информации о заготовке"""
        self.ui.label_blank_width.setText("—")
        self.ui.label_blank_height.setText("—")
        self.ui.label_blank_length.setText("—")
        
        self.ui.spinBox_product_width.setEnabled(False)
        self.ui.spinBox_product_width.setValue(0)
        self.ui.spinBox_product_height.setEnabled(False)
        self.ui.spinBox_product_height.setValue(0)
        self.ui.spinBox_product_length.setEnabled(False)
        self.ui.spinBox_product_length.setValue(0)
    
    def get_blank_data(self):
        """Получение данных заготовок, размеров детали и выбранных работ"""
        if not self.selected_blank:
            return None
        
        # Получаем значение припуска для эрозионных работ
        erosion_offset = self.EROSION_OFFSET  # По умолчанию
        if hasattr(self.ui, 'doubleSpinBox_erosion_offset'):
            erosion_offset = self.ui.doubleSpinBox_erosion_offset.value()
        
        # Возвращаем список заготовок выбранного размера
        return {
            'component_id': self.component['id'],
            'list_blank': self.selected_blank['list_blank'],  # Список всех доступных заготовок этого размера
            'blank_count': self.selected_blank['count'],  # Количество доступных заготовок
            'product_width': self.ui.spinBox_product_width.value() if self.ui.spinBox_product_width.value() > 0 else None,
            'product_height': self.ui.spinBox_product_height.value() if self.ui.spinBox_product_height.value() > 0 else None,
            'product_length': self.ui.spinBox_product_length.value() if self.ui.spinBox_product_length.value() > 0 else None,
            'erosion_offset': erosion_offset,  # Припуск для эрозионных работ
            'work': self.get_selected_work()  # Получаем работы из чекбоксов
        }
