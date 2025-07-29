"""
Главная точка входа для клиента ADITIM Monitor
"""

import sys
from pathlib import Path

# Добавляем src в путь для импортов
sys.path.insert(0, str(Path(__file__).parent.parent))

from PySide6.QtWidgets import QApplication, QSplashScreen
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap

from .main_window import MainWindow
from .api_client import ApiClient
from .references_manager import references_manager


def main():
    
    # Создание приложения
    app = QApplication(sys.argv)
    app.setApplicationName("ADITIM Monitor")
    app.setApplicationVersion("1.0.0")
    
    # Включение высокого DPI масштабирования
    app.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
    
    print("Запуск клиента ADITIM Monitor...")
    
    # Инициализация API клиента
    api_client = ApiClient()
    
    # Настройка менеджера справочников
    references_manager.set_api_client(api_client)
    
    # Загрузка всех справочников при запуске асинхронно
    print("📚 Загрузка справочников...")
    try:
        # Используем синхронную версию для первичной загрузки при старте
        references_manager.load_all_references_sync()
        print("✅ Справочники загружены успешно")
    except Exception as e:
        print(f"❌ Ошибка загрузки справочников: {e}")
        print("⚠️ Приложение будет запущено с ограниченной функциональностью")
    
    # Создание и отображение главного окна
    window = MainWindow()
    window.show()
    
    print("Клиент запущен успешно")
    
    # Запуск приложения
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
