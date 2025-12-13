"""Диалог создания/редактирования типа компонента"""
from PySide6.QtWidgets import QDialog, QMessageBox
from PySide6.QtCore import QFile
from PySide6.QtUiTools import QUiLoader
from ...constant import UI_PATHS_ABS, get_style_path
from ...style_util import load_styles
from ...api_manager import api_manager

class DialogComponentType(QDialog):
    """Диалог для создания или редактирования типа компонента"""
    def __init__(self, parent=None, component_type=None, dimension_id=None):
        super().__init__(parent)
        self.component_type = component_type
        self.dimension_id = dimension_id
        self.is_edit_mode = component_type is not None
        self.load_ui()
        self.setup_ui()
        self.load_dimension_list()
        if self.is_edit_mode:
            self.load_component_type_data()

    def load_ui(self):
        """Загрузка UI из файла"""
        ui_file = QFile(UI_PATHS_ABS["DIALOG_COMPONENT_TYPE"])
        ui_file.open(QFile.ReadOnly)
        loader = QUiLoader()
        self.ui = loader.load(ui_file, self)
        ui_file.close()
        
        # Копируем геометрию и заголовок
        self.setWindowTitle(self.ui.windowTitle())
        self.setGeometry(self.ui.geometry())
        self.setLayout(self.ui.layout())

    def setup_ui(self):
        """Настройка UI компонентов"""
        self.setStyleSheet(load_styles(get_style_path("DIALOGS")))
        
        # Меняем заголовок в зависимости от режима
        if self.is_edit_mode:
            self.setWindowTitle("Редактирование компонента")
        else:
            self.setWindowTitle("Создание компонента")
        
        # Подключаем валидацию
        self.ui.buttonBox.accepted.connect(self.validate_and_accept)
        self.ui.buttonBox.rejected.connect(self.reject)

    def load_dimension_list(self):
        """Загрузка списка размерностей"""
        self.ui.comboBox_dimension.clear()
        list_dimension = api_manager.directory.get('profiletool_dimension', [])
        
        for dimension in list_dimension:
            self.ui.comboBox_dimension.addItem(dimension['name'], dimension['id'])
        
        # Если указана размерность, выбираем её
        if self.dimension_id:
            index = self.ui.comboBox_dimension.findData(self.dimension_id)
            if index >= 0:
                self.ui.comboBox_dimension.setCurrentIndex(index)

    def load_component_type_data(self):
        """Загрузка данных компонента для редактирования"""
        if self.component_type:
            self.ui.lineEdit_name.setText(self.component_type.get('name', ''))
            
            # Выбираем размерность
            dimension_id = self.component_type.get('profiletool_dimension_id')
            if dimension_id:
                index = self.ui.comboBox_dimension.findData(dimension_id)
                if index >= 0:
                    self.ui.comboBox_dimension.setCurrentIndex(index)
            
            # Устанавливаем размеры
            self.ui.spinBox_width.setValue(self.component_type.get('width', 0) or 0)
            self.ui.spinBox_height.setValue(self.component_type.get('height', 0) or 0)
            self.ui.spinBox_length.setValue(self.component_type.get('length', 0) or 0)
            
            # Описание
            self.ui.textEdit_description.setPlainText(self.component_type.get('description', ''))

    def validate_and_accept(self):
        """Валидация данных перед принятием"""
        name = self.ui.lineEdit_name.text().strip()
        
        if not name:
            QMessageBox.warning(self, "Ошибка", "Название не может быть пустым")
            return
        
        if self.ui.comboBox_dimension.currentIndex() < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите тип инструмента")
            return
        
        self.accept()

    def get_component_type_data(self):
        """Получение данных из формы"""
        return {
            "name": self.ui.lineEdit_name.text().strip(),
            "profiletool_dimension_id": self.ui.comboBox_dimension.currentData(),
            "width": self.ui.spinBox_width.value() if self.ui.spinBox_width.value() > 0 else None,
            "height": self.ui.spinBox_height.value() if self.ui.spinBox_height.value() > 0 else None,
            "length": self.ui.spinBox_length.value() if self.ui.spinBox_length.value() > 0 else None,
            "description": self.ui.textEdit_description.toPlainText().strip()
        }
