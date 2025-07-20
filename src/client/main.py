"""
Main entry point for ADITIM Monitor Client
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from .main_window import MainWindow


def main():
    
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("ADITIM Monitor")
    app.setApplicationVersion("1.0.0")
    
    # Enable high DPI scaling
    app.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    print("Client started successfully")
    
    # Run application
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
