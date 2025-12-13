"""Диалог создания/редактирования размерности"""
from PySide6.QtWidgets import QDialog, QMessageBox
from PySide6.QtCore import QFile
from PySide6.QtUiTools import QUiLoader
from ...constant import UI_PATHS_ABS, get_style_path
from ...style_util import load_styles

class DialogDimension(QDialog):
    """Диалог для создания или редактирования размерности"""
    def __init__(self, parent=None, dimension=None):
        super().__init__(parent)
        self.dimension = dimension
        self.is_edit_mode = dimension is not None
        self.load_ui()
        self.setup_ui()
        if self.is_edit_mode:
            self.load_dimension_data()

    def load_ui(self):
        """Загрузка UI из файла"""
        ui_file = QFile(UI_PATHS_ABS["DIALOG_DIMENSION"])
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
            self.setWindowTitle("Редактирование размерности")
        else:
            self.setWindowTitle("Создание размерности")
        
        # Подключаем валидацию
        self.ui.buttonBox.accepted.connect(self.validate_and_accept)
        self.ui.buttonBox.rejected.connect(self.reject)

    def load_dimension_data(self):
        """Загрузка данных размерности для редактирования"""
        if self.dimension:
            self.ui.lineEdit_name.setText(self.dimension.get('name', ''))
            self.ui.textEdit_description.setPlainText(self.dimension.get('description', ''))

    def validate_and_accept(self):
        """Валидация данных перед принятием"""
        name = self.ui.lineEdit_name.text().strip()
        
        if not name:
            QMessageBox.warning(self, "Ошибка", "Название не может быть пустым")
            return
        
        self.accept()

    def get_dimension_data(self):
        """Получение данных из формы"""
        return {
            "name": self.ui.lineEdit_name.text().strip(),
            "description": self.ui.textEdit_description.toPlainText().strip()
        }
