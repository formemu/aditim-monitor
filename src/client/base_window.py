"""Базовый класс для всех окон приложения ADITIM Monitor."""
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import QFile, Qt
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QPixmap
from .constant import ICON_PATHS_ABS, get_style_path
from .style_util import load_styles


class BaseWindow(QWidget):
    """Базовый класс для всех окон приложения.
    
    Обеспечивает единообразную инициализацию:
    - Загрузка UI из .ui файла
    - Применение стилей
    - Загрузка логотипа ADITIM
    - Автоматическое подключение к обновлениям данных
    
    Подклассы должны переопределить:
    - setup_ui() — настройка специфичных для окна элементов
    - refresh_data() — обновление данных в окне
    """
    
    def __init__(self, ui_path: str, api_manager, parent=None):
        """Инициализация базового окна.
        
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
        
        # Подключаемся к обновлениям данных
        self.api_manager.data_updated.connect(self.refresh_data)
    
    def load_ui(self):
        """Загрузка UI из файла.
        
        Стандартная реализация через QUiLoader.
        Переопределение обычно не требуется.
        """
        ui_file = QFile(self.ui_path)
        ui_file.open(QFile.ReadOnly)
        
        loader = QUiLoader()
        self.ui = loader.load(ui_file)
        
        ui_file.close()
    
    def setup_ui(self):
        """Настройка UI компонентов.
        
        Должна быть переопределена в подклассах для:
        - Применения стилей
        - Подключения сигналов к слотам
        - Настройки специфичных элементов
        - Вызова load_logo()
        - Первичной загрузки данных
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} должен переопределить метод setup_ui()"
        )
    
    def load_logo(self):
        """Загрузка логотипа ADITIM.
        
        Стандартная реализация для label_logo.
        Если в окне нет логотипа или используется другое имя виджета,
        можно переопределить или не вызывать.
        """
        logo_path = ICON_PATHS_ABS.get("ADITIM_LOGO_MAIN")
        if not logo_path:
            return
        
        # Проверяем наличие label_logo в UI
        if not hasattr(self.ui, 'label_logo'):
            return
        
        pixmap = QPixmap(logo_path)
        scaled = pixmap.scaled(
            300, 100,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.ui.label_logo.setPixmap(scaled)
        self.ui.label_logo.setText("")
    
    def refresh_data(self):
        """Обновление данных в окне.
        
        Вызывается автоматически при изменении данных в api_manager.
        Должна быть переопределена в подклассах для обновления
        специфичных для окна данных.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} должен переопределить метод refresh_data()"
        )
    
    def apply_styles(self):
        """Применение стандартных стилей.
        
        Удобный метод для применения стилей из константы MAIN.
        Вызывается в setup_ui() подклассов.
        """
        self.ui.setStyleSheet(load_styles(get_style_path("MAIN")))
