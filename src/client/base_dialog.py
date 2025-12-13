"""Базовый класс для всех диалогов приложения ADITIM Monitor."""
from PySide6.QtWidgets import QDialog
from PySide6.QtCore import QFile
from PySide6.QtUiTools import QUiLoader


class BaseDialog(QDialog):
    """Базовый класс для всех диалогов приложения.
    
    Обеспечивает единообразную инициализацию:
    - Загрузка UI из .ui файла
    - Правильная установка layout для диалога
    - Доступ к api_manager
    
    Подклассы должны переопределить:
    - setup_ui() — настройка специфичных для диалога элементов
    """
    
    def __init__(self, ui_path: str, api_manager, parent=None):
        """Инициализация базового диалога.
        
        Args:
            ui_path: Путь к .ui файлу
            api_manager: Экземпляр API менеджера
            parent: Родительский виджет
        """
        super().__init__(parent)
        self.ui_path = ui_path
        self.api_manager = api_manager
        self.ui = None
        
        # Загружаем UI
        self.load_ui()
        
        # Настраиваем UI (переопределяется в подклассах)
        self.setup_ui()
    
    def load_ui(self):
        """Загрузка UI из файла.
        
        Стандартная реализация через QUiLoader с установкой layout.
        Переопределение обычно не требуется.
        """
        ui_file = QFile(self.ui_path)
        ui_file.open(QFile.ReadOnly)
        
        loader = QUiLoader()
        self.ui = loader.load(ui_file, self)
        
        ui_file.close()
        
        # Устанавливаем layout для правильного отображения диалога
        if self.ui.layout():
            self.setLayout(self.ui.layout())
    
    def setup_ui(self):
        """Настройка UI компонентов.
        
        Должна быть переопределена в подклассах для:
        - Подключения сигналов к слотам
        - Настройки специфичных элементов
        - Подключения buttonBox к accept/reject
        - Установки начальных значений
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} должен переопределить метод setup_ui()"
        )
