"""
Главное окно для ADITIM Monitor Client
"""

from PySide6.QtWidgets import QMainWindow, QMessageBox
from PySide6.QtCore import QFile
from PySide6.QtUiTools import QUiLoader

from .resources import UI_PATHS


class MainWindow(QMainWindow):
    """Главное окно приложения"""
    
    def __init__(self):
        super().__init__()
        self.load_ui()
        self.setup_ui()

    def load_ui(self):
        """Загрузка UI из файла"""
        ui_file = QFile(UI_PATHS["MAIN_WINDOW"])
        ui_file.open(QFile.ReadOnly)
        
        loader = QUiLoader()
        self.ui = loader.load(ui_file)
        ui_file.close()

        self.setWindowTitle(self.ui.windowTitle())
        self.setGeometry(self.ui.geometry())
        self.setMenuBar(self.ui.menubar)
        self.setStatusBar(self.ui.statusbar)
        self.setCentralWidget(self.ui.centralwidget)

    def setup_ui(self):
        """Настройка UI компонентов после загрузки"""
        self.ui.pushButton_test.clicked.connect(self.on_test_clicked)

    def on_test_clicked(self):
        """Обработка нажатия тестовой кнопки"""
        QMessageBox.information(self, "Тест", "Главное окно работает!")
