"""
Main entry point for ADITIM Monitor Client
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from PySide6.QtWidgets import QApplication, QSplashScreen
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap

from .main_window import MainWindow
from .api_client import ApiClient
from .references_manager import references_manager


def main():
    
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("ADITIM Monitor")
    app.setApplicationVersion("1.0.0")
    
    # Enable high DPI scaling
    app.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
    
    print("Starting ADITIM Monitor Client...")
    
    # Initialize API client
    api_client = ApiClient()
    
    # Set up references manager
    references_manager.set_api_client(api_client)
    
    # Load all references at startup
    print("📚 Загрузка справочников...")
    try:
        references_manager.load_all_references_sync()
        print("✅ Справочники загружены успешно")
    except Exception as e:
        print(f"❌ Ошибка загрузки справочников: {e}")
        print("⚠️ Приложение будет запущено с ограниченной функциональностью")
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    print("Client started successfully")
    
    # Run application
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
