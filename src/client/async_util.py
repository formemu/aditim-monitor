"""
Утилиты для асинхронных операций в Qt приложении
"""

from PySide6.QtCore import QRunnable, QObject, Signal, QThreadPool
from typing import Callable


class WorkerSignal(QObject):
    """Сигналы для рабочего класса"""
    finished = Signal(object)  # Успешное завершение с результатом
    error = Signal(Exception)  # Ошибка выполнения


class AsyncWorker(QRunnable):
    """Рабочий класс для выполнения асинхронных операций"""
    
    def __init__(self, func: Callable, on_success: Callable = None, on_error: Callable = None, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignal()
        
        # Подключаем callbacks
        if on_success:
            self.signals.finished.connect(on_success)
        if on_error:
            self.signals.error.connect(on_error)
    
    def run(self):
        """Выполнение функции в рабочем потоке"""
        try:
            result = self.func(*self.args, **self.kwargs)
            self.signals.finished.emit(result)
        except Exception as e:
            self.signals.error.emit(e)


def run_async(func: Callable, on_success: Callable = None, on_error: Callable = None, *args, **kwargs):
    """
    Запускает функцию асинхронно в пуле потоков
    
    Args:
        func: Функция для выполнения
        on_success: Callback для успешного результата
        on_error: Callback для обработки ошибок
        *args, **kwargs: Аргументы для функции
    
    Returns:
        worker: объект worker для управления выполнением
    """
    # Создаем worker
    worker = AsyncWorker(func, on_success, on_error, *args, **kwargs)
    
    # Запускаем в пуле потоков
    QThreadPool.globalInstance().start(worker)
    
    return worker
