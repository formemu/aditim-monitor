"""Диалог создания/редактирования размерности"""
from PySide6.QtWidgets import QMessageBox

from ...base_dialog import BaseDialog
from ...constant import UI_PATHS_ABS, get_style_path
from ...style_util import load_styles
from ...api_manager import api_manager


class DialogDimension(BaseDialog):
    """Диалог для создания или редактирования размерности"""
    def __init__(self, parent=None, dimension=None):
        self.dimension = dimension
        self.is_edit_mode = dimension is not None
        super().__init__(UI_PATHS_ABS["DIALOG_DIMENSION"], api_manager, parent)
        if self.is_edit_mode:
            self.load_dimension_data()
        
        # Копируем заголовок и геометрию из UI
        self.setWindowTitle(self.ui.windowTitle())
        self.setGeometry(self.ui.geometry())

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
