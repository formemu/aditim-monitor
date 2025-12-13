# ✅ Чек-лист миграции на базовые классы

## 📊 Прогресс

**Базовые классы:** ✅ Готовы  
**Примеры:** ✅ window_profile.py, dialog_create_profile.py  
**Документация:** ✅ MIGRATION_GUIDE.md, BASE_CLASSES_DOCS.md  
**Тестирование:** ✅ Клиент запускается без ошибок
**Мигрировано:** ✅ 18/27+ файлов (67%)
**Экономия кода:** ✅ -544 строки

---

## 🪟 Windows (7 файлов)

### ✅ Завершено (7/7) — 100%
- [x] `window_profile.py` — ✅ -31 строка
- [x] `window_machine.py` — ✅ -31 строка
- [x] `window_setting.py` — ✅ -31 строка
- [x] `window_task.py` — ✅ -31 строка
- [x] `window_blank.py` — ✅ -31 строка
- [x] `window_development.py` — ✅ -35 строк
- [x] `window_product.py` — ✅ -31 строка

**Экономия:** -221 строка

---

## 💬 Dialogs (20+ файлов)

### ✅ Завершено (11/20)
- [x] `dialog_create_profile.py` — ✅ -27 строк
- [x] `dialog_edit_profile.py` — ✅ -29 строк
- [x] `dialog_create_product.py` — ✅ -30 строк
- [x] `dialog_edit_product.py` — ✅ -30 строк
- [x] `dialog_create_profiletool.py` — ✅ -30 строк
- [x] `dialog_edit_profiletool.py` — ✅ -30 строк
- [x] `dialog_dimension.py` — ✅ -28 строк
- [x] `dialog_component_type.py` — ✅ -32 строки
- [x] `dialog_plan_stage.py` — ✅ -32 строки
- [x] `dialog_create_blank.py` — ✅ -28 строк
- [x] `dialog_create_profiletool_component.py` — ✅ -27 строк

**Экономия:** -323 строки

---

## 📋 Процесс миграции

### Для каждого файла:

1. **Изучить файл**
   - [ ] Прочитать полностью
   - [ ] Понять структуру
   - [ ] Найти специфичную логику

2. **Изменить импорты**
   - [ ] Удалить: QWidget/QDialog, QFile, QUiLoader
   - [ ] Добавить: BaseWindow/BaseDialog
   - [ ] Проверить остальные импорты

3. **Изменить класс**
   - [ ] Наследоваться от BaseWindow/BaseDialog
   - [ ] Переместить инициализацию полей перед super().__init__()
   - [ ] Передать ui_path и api_manager в super().__init__()

4. **Удалить дублирующийся код**
   - [ ] Удалить метод load_ui()
   - [ ] Удалить метод load_logo() (для windows)
   - [ ] Удалить ручное подключение к data_updated (для windows)

5. **Обновить setup_ui()**
   - [ ] Заменить прямую установку стилей на apply_styles()
   - [ ] Убедиться, что load_logo() вызывается (для windows)
   - [ ] Проверить порядок инициализации

6. **Тестирование**
   - [ ] Запустить get_errors
   - [ ] Запустить клиент
   - [ ] Проверить работу окна/диалога
   - [ ] Закоммитить изменения

---

## 🎯 Порядок миграции (рекомендуемый)

### Этап 1: Простые окна (2-3 дня)
1. window_machine.py (самое простое)
2. window_setting.py
3. window_task.py

### Этап 2: Сложные окна (3-5 дней)
4. window_blank.py
5. window_development.py
6. window_product.py (самое сложное)

### Этап 3: Простые диалоги (3-5 дней)
7-9. Все dialog_edit_* файлы (они похожи на dialog_create_*)

### Этап 4: Сложные диалоги (5-7 дней)
10-15. Диалоги с таблицами и сложной логикой

### Этап 5: Особые случаи (2-3 дня)
16+. Wizard и другие нестандартные виджеты

---

## 📝 Шаблон для миграции Window

```python
# ❌ Старый код
class WindowSomething(QWidget):
    def __init__(self):
        super().__init__()
        self.item = None
        self.load_ui()
        self.setup_ui()
        api_manager.data_updated.connect(self.refresh_data)
    
    def load_ui(self):
        ui_file = QFile(UI_PATHS_ABS["SOMETHING"])
        ui_file.open(QFile.ReadOnly)
        loader = QUiLoader()
        self.ui = loader.load(ui_file)
        ui_file.close()
    
    def setup_ui(self):
        self.ui.setStyleSheet(load_styles(get_style_path("MAIN")))
        self.load_logo()
        # ... специфичная логика
    
    def load_logo(self):
        logo_path = ICON_PATHS_ABS.get("ADITIM_LOGO_MAIN")
        pixmap = QPixmap(logo_path)
        scaled = pixmap.scaled(300, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.ui.label_logo.setPixmap(scaled)
        self.ui.label_logo.setText("")

# ✅ Новый код
class WindowSomething(BaseWindow):
    def __init__(self):
        self.item = None
        super().__init__(UI_PATHS_ABS["SOMETHING"], api_manager)
    
    def setup_ui(self):
        self.apply_styles()
        self.load_logo()
        # ... специфичная логика (без изменений)
```

---

## 📝 Шаблон для миграции Dialog

```python
# ❌ Старый код
class DialogSomething(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.data = None
        self.load_ui()
        self.setup_ui()
    
    def load_ui(self):
        ui_file = QFile(UI_PATHS_ABS["DIALOG_SOMETHING"])
        ui_file.open(QFile.ReadOnly)
        loader = QUiLoader()
        self.ui = loader.load(ui_file, self)
        ui_file.close()
        self.setLayout(self.ui.layout())
    
    def setup_ui(self):
        self.ui.buttonBox.accepted.connect(self.accept)
        # ... специфичная логика

# ✅ Новый код
class DialogSomething(BaseDialog):
    def __init__(self, parent):
        self.data = None
        super().__init__(UI_PATHS_ABS["DIALOG_SOMETHING"], api_manager, parent)
    
    def setup_ui(self):
        self.ui.buttonBox.accepted.connect(self.accept)
        # ... специфичная логика (без изменений)
```

---

## 🚨 Типичные ошибки

### ❌ Инициализация полей после super().__init__()
```python
# НЕПРАВИЛЬНО
def __init__(self):
    super().__init__(UI_PATHS_ABS["SOMETHING"], api_manager)
    self.item = None  # ❌ setup_ui() уже вызван, поздно!
```

```python
# ПРАВИЛЬНО
def __init__(self):
    self.item = None  # ✅ До super().__init__()
    super().__init__(UI_PATHS_ABS["SOMETHING"], api_manager)
```

### ❌ Забыли удалить load_ui()
```python
# НЕПРАВИЛЬНО
class WindowSomething(BaseWindow):
    def load_ui(self):  # ❌ Дублирование!
        # ... код загрузки UI
```

### ❌ Забыли изменить импорты
```python
# НЕПРАВИЛЬНО
from PySide6.QtWidgets import QWidget  # ❌ Не нужен!
from ..base_window import BaseWindow

class WindowSomething(BaseWindow):
    pass
```

---

## 📊 Метрики успеха

- [ ] Все 7 windows мигрированы
- [ ] Все 20+ dialogs мигрированы
- [ ] Клиент запускается без ошибок
- [ ] Все функции работают как раньше
- [ ] Код сокращён на ~500 строк
- [ ] Нет дублирования логики загрузки UI
