from PySide6.QtCore import QThread, Signal
from typing import Callable, Any

class WorkerThread(QThread):
    """
    Класс для выполнения функции в отдельном потоке с передачей результата через сигналы.
    """
    finished = Signal(object)
    error = Signal(str)

    def __init__(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> None:
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def run(self) -> None:
        try:
            result = self.func(*self.args, **self.kwargs)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))
