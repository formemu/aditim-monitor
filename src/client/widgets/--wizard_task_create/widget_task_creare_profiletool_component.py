from PySide6.QtWidgets import QWidget
from PySide6.QtCore import QFile
from PySide6.QtUiTools import QUiLoader
from ...constant import UI_PATHS_ABS


class WidgetTaskCreateProfiletoolComponent(QWidget):
    """Виджет создания компонента инструмента профиля"""
    def __init__(self, component: dict, parent=None):
        super().__init__(parent)
        self.component = component
        self.load_ui()
        self.setup_ui()
    
    def load_ui(self):
        """Загрузка UI из файла"""
        ui_file = QFile(UI_PATHS_ABS["WIDGET_TASK_CREATE_PROFILETOOL_COMPONENT"])
        ui_file.open(QFile.ReadOnly)
        loader = QUiLoader()
        self.ui = loader.load(ui_file)
        ui_file.close()
        self.setLayout(self.ui.layout())

    def setup_ui(self):
        """Настраивает логику визарда."""

