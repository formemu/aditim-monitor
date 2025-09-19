"""Главная точка входа для клиента ADITIM Monitor"""

import sys
import asyncio
import qasync
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from .main_window import MainWindow
from .api_manager import api_manager


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("ADITIM Monitor")
    app.setApplicationVersion("1.0.0")

    # DPI
    app.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)

    window = MainWindow()
    window.show()

    # Запуск асинхронного цикла
    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)

    with loop:
        loop.call_soon(api_manager.load_all_async)           # старт загрузки
        loop.call_later(0.1, api_manager.start_websocket_listener)  # старт вебсокета
        
        loop.run_forever()



if __name__ == "__main__":
    sys.exit(main())