# 📚 Руководство по миграции на базовые классы

## ✅ Что сделано

### Созданы базовые классы:
- **`base_window.py`** — для всех окон (windows/*.py)
- **`base_dialog.py`** — для всех диалогов (widgets/**/dialog_*.py)

### Примеры рефакторинга:
- ✅ **`window_profile.py`** — мигрировано на BaseWindow
- ✅ **`dialog_create_profile.py`** — мигрировано на BaseDialog

### Проверено:
- ✅ Нет ошибок компиляции
- ✅ Клиент запускается успешно
- ✅ WebSocket подключение работает

---

## 🎯 Преимущества

### До рефакторинга (window_profile.py — 151 строка):
```python
class WindowProfile(QWidget):
    def __init__(self):
        super().__init__()
        self.profile = None
        self.load_ui()
        self.setup_ui()
        api_manager.data_updated.connect(self.refresh_data)
    
    def load_ui(self):
        """17 строк дублирующегося кода"""
        ui_file = QFile(UI_PATHS_ABS["PROFILE_CONTENT"])
        ui_file.open(QFile.ReadOnly)
        loader = QUiLoader()
        self.ui = loader.load(ui_file)
        ui_file.close()
    
    def load_logo(self):
        """12 строк дублирующегося кода"""
        logo_path = ICON_PATHS_ABS.get("ADITIM_LOGO_MAIN")
        pixmap = QPixmap(logo_path)
        scaled = pixmap.scaled(300, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.ui.label_logo.setPixmap(scaled)
        self.ui.label_logo.setText("")
```

### После рефакторинга (window_profile.py — 120 строк, -20%):
```python
class WindowProfile(BaseWindow):
    def __init__(self):
        self.profile = None
        super().__init__(UI_PATHS_ABS["PROFILE_CONTENT"], api_manager)
    
    # load_ui() — унаследован из BaseWindow
    # load_logo() — унаследован из BaseWindow
```

**Экономия: -31 строка кода на каждое окно!**

---

## 🔄 Как мигрировать Windows

### Шаг 1: Изменить импорты
```python
# ❌ Было
from PySide6.QtWidgets import QWidget, QMessageBox, QTableWidgetItem
from PySide6.QtCore import QFile, Qt
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QPixmap
from ..constant import UI_PATHS_ABS, ICON_PATHS_ABS, get_style_path
from ..style_util import load_styles

# ✅ Стало
from PySide6.QtWidgets import QMessageBox, QTableWidgetItem
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from ..base_window import BaseWindow
from ..constant import UI_PATHS_ABS
```

### Шаг 2: Изменить класс
```python
# ❌ Было
class WindowProfile(QWidget):
    def __init__(self):
        super().__init__()
        self.profile = None
        self.load_ui()
        self.setup_ui()
        api_manager.data_updated.connect(self.refresh_data)

# ✅ Стало
class WindowProfile(BaseWindow):
    def __init__(self):
        self.profile = None
        super().__init__(UI_PATHS_ABS["PROFILE_CONTENT"], api_manager)
```

### Шаг 3: Удалить load_ui() и load_logo()
```python
# ❌ Удалить эти методы — они теперь в BaseWindow
def load_ui(self):
    ...

def load_logo(self):
    ...
```

### Шаг 4: Обновить setup_ui()
```python
# ❌ Было
def setup_ui(self):
    self.ui.setStyleSheet(load_styles(get_style_path("MAIN")))
    self.load_logo()
    # ... остальной код

# ✅ Стало
def setup_ui(self):
    self.apply_styles()  # Новый метод из BaseWindow
    self.load_logo()     # Унаследован из BaseWindow
    # ... остальной код
```

---

## 🔄 Как мигрировать Dialogs

### Шаг 1: Изменить импорты
```python
# ❌ Было
from PySide6.QtWidgets import QDialog, QMessageBox
from PySide6.QtCore import QFile, QBuffer, Qt
from PySide6.QtUiTools import QUiLoader

# ✅ Стало
from PySide6.QtWidgets import QMessageBox
from PySide6.QtCore import QBuffer, Qt
from ...base_dialog import BaseDialog
```

### Шаг 2: Изменить класс
```python
# ❌ Было
class DialogCreateProfile(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.sketch_data = None
        self.load_ui()
        self.setup_ui()

# ✅ Стало
class DialogCreateProfile(BaseDialog):
    def __init__(self, parent):
        self.sketch_data = None
        super().__init__(UI_PATHS_ABS["DIALOG_CREATE_PROFILE"], api_manager, parent)
```

### Шаг 3: Удалить load_ui()
```python
# ❌ Удалить этот метод — он теперь в BaseDialog
def load_ui(self):
    ui_file = QFile(UI_PATHS_ABS["DIALOG_CREATE_PROFILE"])
    ui_file.open(QFile.ReadOnly)
    loader = QUiLoader()
    self.ui = loader.load(ui_file, self)
    ui_file.close()
    self.setLayout(self.ui.layout())
```

---

## 📋 Список файлов для миграции

### Windows (осталось 6 файлов):
- [ ] `window_product.py`
- [ ] `window_task.py`
- [ ] `window_blank.py`
- [ ] `window_development.py`
- [ ] `window_machine.py`
- [ ] `window_setting.py`

### Dialogs (осталось ~20 файлов):
- [ ] `dialog_edit_profile.py`
- [ ] `dialog_create_product.py`
- [ ] `dialog_edit_product.py`
- [ ] `dialog_create_profiletool.py`
- [ ] `dialog_edit_profiletool.py`
- [ ] `dialog_create_profiletool_component.py`
- [ ] `dialog_create_blank.py`
- [ ] `dialog_dimension.py`
- [ ] `dialog_plan_stage.py`
- [ ] `dialog_component_type.py`
- И другие...

---

## 💡 Советы

1. **Мигрируй по одному файлу** — так проще проверять работу
2. **Запускай клиент после каждой миграции** — убедись, что всё работает
3. **Используй get_errors** — проверяй отсутствие ошибок компиляции
4. **Сохраняй логику** — меняй только наследование, не трогай бизнес-логику

---

## ⚠️ Особые случаи

### Если в окне нет логотипа:
```python
def setup_ui(self):
    self.apply_styles()
    # Не вызываем self.load_logo() — его нет в этом окне
    # ... остальной код
```

### Если используется другой стиль:
```python
def setup_ui(self):
    # Не используем apply_styles(), применяем свой стиль
    self.ui.setStyleSheet(load_styles(get_style_path("CUSTOM")))
    # ... остальной код
```

### Если диалог не использует api_manager:
```python
# В __init__ передаём None вместо api_manager
super().__init__(UI_PATHS_ABS["SOME_DIALOG"], None, parent)
```

---

## 🎉 Ожидаемый результат

После миграции всех файлов:
- **-500+ строк дублирующегося кода**
- **100% единообразие** в загрузке UI
- **Проще поддержка** — изменения в одном месте
- **Быстрее разработка** — меньше boilerplate кода
