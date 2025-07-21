"""
Утилиты для асинхронных операций в Qt приложении
"""

from PySide6.QtCore import QThread, QObject, Signal
from typing import Callable, Any


class AsyncWorker(QObject):
    """Рабочий класс для выполнения асинхронных операций"""
    
    # Сигналы для результатов
    finished = Signal(object)  # Успешное завершение с результатом
    error = Signal(Exception)  # Ошибка выполнения
    
    def __init__(self, func: Callable, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
    
    def run(self):
        """Выполнение функции в рабочем потоке"""
        try:
            result = self.func(*self.args, **self.kwargs)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(e)


def run_async(func: Callable, on_success: Callable = None, on_error: Callable = None, *args, **kwargs):
    """
    Запускает функцию асинхронно в отдельном потоке
    
    Args:
        func: Функция для выполнения
        on_success: Callback для успешного результата
        on_error: Callback для обработки ошибок
        *args, **kwargs: Аргументы для функции
    
    Returns:
        tuple: (thread, worker) для управления выполнением
    """
    # Создаем поток и рабочий объект
    thread = QThread()
    worker = AsyncWorker(func, *args, **kwargs)
    
    # Перемещаем worker в поток
    worker.moveToThread(thread)
    
    # Подключаем сигналы
    thread.started.connect(worker.run)
    
    if on_success:
        worker.finished.connect(on_success)
    if on_error:
        worker.error.connect(on_error)
    
    # Правильная очистка ресурсов
    def cleanup():
        worker.deleteLater()
        thread.quit()
        thread.wait()  # Ждем завершения потока
        thread.deleteLater()
    
    worker.finished.connect(cleanup)
    worker.error.connect(cleanup)
    
    # Запускаем поток
    thread.start()
    
    return thread, worker
