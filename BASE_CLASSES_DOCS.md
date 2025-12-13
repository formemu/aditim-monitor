# 📖 Документация базовых классов

## BaseWindow

### Назначение
Базовый класс для всех главных окон приложения (windows/*.py).

### Что предоставляет
- ✅ Автоматическая загрузка .ui файлов
- ✅ Стандартизированная загрузка логотипа ADITIM
- ✅ Автоматическое подключение к обновлениям данных
- ✅ Удобный метод apply_styles()

### Конструктор
```python
BaseWindow(ui_path: str, api_manager, parent=None)
```

**Параметры:**
- `ui_path` — абсолютный путь к .ui файлу (из UI_PATHS_ABS)
- `api_manager` — экземпляр API менеджера (для доступа к данным)
- `parent` — родительский виджет (опционально)

### Методы для переопределения

#### setup_ui()
**Обязательно переопределить!**

Настройка UI элементов после загрузки:
- Применение стилей через `self.apply_styles()`
- Загрузка логотипа через `self.load_logo()`
- Подключение сигналов к слотам
- Первичная загрузка данных через `self.refresh_data()`

```python
def setup_ui(self):
    self.apply_styles()
    self.load_logo()
    
    # Подключаем кнопки
    self.ui.pushButton_add.clicked.connect(self.on_add_clicked)
    self.ui.pushButton_edit.clicked.connect(self.on_edit_clicked)
    
    # Загружаем данные
    self.refresh_data()
```

#### refresh_data()
**Обязательно переопределить!**

Обновление данных в окне. Вызывается автоматически при изменении данных в api_manager.

```python
def refresh_data(self):
    # Сбрасываем выбранный элемент
    self.selected_item = None
    
    # Обновляем таблицу
    self.update_table()
    
    # Очищаем панель информации
    self.clear_info_panel()
```

### Методы, которые можно использовать

#### apply_styles()
Применяет стандартные стили из константы MAIN.

```python
def setup_ui(self):
    self.apply_styles()  # Применяет стили из get_style_path("MAIN")
    # ...
```

#### load_logo()
Загружает логотип ADITIM в `label_logo`.

Можно не вызывать, если в окне нет логотипа.

```python
def setup_ui(self):
    self.load_logo()  # Загружает ADITIM_LOGO_MAIN в label_logo
    # ...
```

### Доступные атрибуты

- `self.ui` — загруженный UI виджет (доступ к элементам: `self.ui.pushButton_save`)
- `self.api_manager` — API менеджер для работы с данными
- `self.ui_path` — путь к .ui файлу

### Пример использования

```python
from ..base_window import BaseWindow
from ..constant import UI_PATHS_ABS
from ..api_manager import api_manager

class WindowProfile(BaseWindow):
    def __init__(self):
        self.profile = None
        super().__init__(UI_PATHS_ABS["PROFILE_CONTENT"], api_manager)
    
    def setup_ui(self):
        # Стандартная настройка
        self.apply_styles()
        self.load_logo()
        
        # Подключаем сигналы
        self.ui.pushButton_add.clicked.connect(self.on_add_clicked)
        
        # Загружаем данные
        self.refresh_data()
    
    def refresh_data(self):
        # Обновляем таблицу
        self.update_table()
    
    def on_add_clicked(self):
        # Обработчик кнопки
        pass
```

---

## BaseDialog

### Назначение
Базовый класс для всех диалоговых окон (widgets/**/dialog_*.py).

### Что предоставляет
- ✅ Автоматическая загрузка .ui файлов
- ✅ Правильная установка layout для диалога
- ✅ Доступ к api_manager

### Конструктор
```python
BaseDialog(ui_path: str, api_manager, parent=None)
```

**Параметры:**
- `ui_path` — абсолютный путь к .ui файлу (из UI_PATHS_ABS)
- `api_manager` — экземпляр API менеджера (может быть None)
- `parent` — родительский виджет (обычно окно, из которого открыт диалог)

### Методы для переопределения

#### setup_ui()
**Обязательно переопределить!**

Настройка UI элементов после загрузки:
- Подключение кнопок buttonBox к accept/reject
- Подключение других сигналов к слотам
- Установка начальных значений полей
- Настройка фокуса

```python
def setup_ui(self):
    # Подключаем стандартные кнопки
    self.ui.buttonBox.accepted.connect(self.accept)
    self.ui.buttonBox.rejected.connect(self.reject)
    
    # Подключаем свои обработчики
    self.ui.pushButton_load.clicked.connect(self.on_load_clicked)
    
    # Устанавливаем фокус
    self.ui.lineEdit_name.setFocus()
```

### Доступные атрибуты

- `self.ui` — загруженный UI виджет (доступ к элементам: `self.ui.lineEdit_name`)
- `self.api_manager` — API менеджер для работы с данными
- `self.ui_path` — путь к .ui файлу

### Пример использования

```python
from ...base_dialog import BaseDialog
from ...api_manager import api_manager
from ...constant import UI_PATHS_ABS

class DialogCreateProfile(BaseDialog):
    def __init__(self, parent):
        self.sketch_data = None
        super().__init__(UI_PATHS_ABS["DIALOG_CREATE_PROFILE"], api_manager, parent)
    
    def setup_ui(self):
        # Подключаем стандартные кнопки
        self.ui.buttonBox.accepted.connect(self.accept)
        self.ui.buttonBox.rejected.connect(self.reject)
        
        # Подключаем свои кнопки
        self.ui.pushButton_paste.clicked.connect(self.on_paste_clicked)
        
        # Устанавливаем фокус
        self.ui.lineEdit_article.setFocus()
    
    def accept(self):
        # Валидация перед закрытием
        if self.validate_data():
            self.create_profile()
            super().accept()
    
    def validate_data(self):
        # Проверка данных
        return True
    
    def create_profile(self):
        # Создание профиля
        profile_data = {
            "article": self.ui.lineEdit_article.text(),
            # ...
        }
        self.api_manager.api_profile.create_profile(profile_data)
```

---

## Частые вопросы

### Q: Что если в диалоге не нужен api_manager?
A: Передайте None:
```python
super().__init__(UI_PATHS_ABS["SOME_DIALOG"], None, parent)
```

### Q: Что если нужен другой стиль, не MAIN?
A: Не используйте `apply_styles()`, примените свой:
```python
def setup_ui(self):
    self.ui.setStyleSheet(load_styles(get_style_path("CUSTOM")))
    # ...
```

### Q: Что если в окне нет логотипа?
A: Просто не вызывайте `load_logo()`:
```python
def setup_ui(self):
    self.apply_styles()
    # Не вызываем load_logo()
    # ...
```

### Q: Нужно ли переопределять load_ui()?
A: Нет! Стандартная реализация подходит для 99% случаев.

### Q: Можно ли добавить свои методы в подклассе?
A: Конечно! Базовые классы не ограничивают функциональность.
