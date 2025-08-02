"""
Главная точка входа для клиента ADITIM Monitor
"""

import sys

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from .main_window import MainWindow
from .references_manager import references_manager


def main():
    
    # Создание приложения
    app = QApplication(sys.argv)
    app.setApplicationName("ADITIM Monitor")
    app.setApplicationVersion("1.0.0")
    
    # Включение высокого DPI масштабирования
    app.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
    
    references_manager.load_all_references_sync()

    # Создание и отображение главного окна
    window = MainWindow()
    window.show()
    
    
    # Запуск приложения
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
