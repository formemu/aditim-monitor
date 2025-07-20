<!-- Используйте этот файл для предоставления пользовательских инструкций для Copilot, специфичных для рабочей области. Для получения дополнительной информации посетите https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# ADITIM Monitor - Инструкции для ИИ-агента программирования

## Соглашения стиля кода

### 🧱 Общие принципы дизайна
- **UI-FIRST**: Все элементы пользовательского интерфейса должны создаваться с использованием .ui файлов, а не программно. Используйте Qt Designer для всех макетов, виджетов и визуальных компонентов. Код должен обрабатывать только бизнес-логику, привязку данных и обработку событий.
- **SOLID**: Код должен быть открыт для расширения, закрыт для модификации. Разделяйте ответственность между классами
- **DRY (Don't Repeat Yourself)**: Избегайте дублирования логики. Выносите повторяющиеся фрагменты в отдельные методы или классы
- **KISS (Keep It Simple, Stupid)**: Не усложняйте. Простой и понятный код - приоритет

### Стандарты Python
- **Инструменты**: Используйте `black`, `flake8`, `mypy` для форматирования и проверки кода
- **Отступы**: 4 пробела
- **Соглашения именования**:
  - Классы: CamelCase (`TaskManager`, `ProfileDialog`)
  - Функции и переменные: snake_case (`get_task_list`, `current_status`)
  - Константы: UPPER_SNAKE_CASE (`MAX_ACTIVE_TASKS`, `DEFAULT_STATUS`)
- **Длина строки**: Максимум 79 символов
- **Пустые строки**:
  - Одна пустая строка между методами
  - Две пустые строки между классами
- **Docstrings**: Добавляйте docstring к каждому классу и публичному методу
- **Аннотации типов**: Обязательны для всех функций

### 🔧 Паттерны PySide6

#### 📦 Импорты
```python
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout
```
Используйте явные импорты вместо `import *`

#### 🏗️ Создание виджетов - подход UI-FIRST
- **ВСЕ UI элементы должны создаваться в .ui файлах с помощью Qt Designer**
- Код НЕ должен создавать виджеты программно (никаких QPushButton(), QLabel() и т.д. в коде)
- Используйте `QUiLoader` для загрузки .ui файлов и прямой доступ к элементам
- Только привязка данных, обработка событий и бизнес-логика должны быть в коде

#### 🏷️ Соглашения именования UI элементов
Все UI элементы в .ui файлах должны следовать стандарту Qt Designer: `widgetType_context_action`

**Стандартный паттерн именования:**
- `pushButton_context_action` - Кнопки (pushButton_task_add, pushButton_profile_delete, pushButton_save)
- `label_context` - Метки (label_title, label_logo, label_status, label_info)  
- `tableWidget_context` - Таблицы (tableWidget_tasks, tableWidget_profiles, tableWidget_products)
- `lineEdit_context` - Поля ввода (lineEdit_article, lineEdit_name, lineEdit_deadline)
- `comboBox_context` - Выпадающие списки (comboBox_status, comboBox_department, comboBox_type)
- `listWidget_context` - Списки (listWidget_equipment, listWidget_components, listWidget_tasks)
- `textEdit_context` - Текстовые поля (textEdit_description, textEdit_notes, textEdit_details)
- `checkBox_context` - Флажки (checkBox_urgent, checkBox_active, checkBox_completed)
- `radioButton_context` - Радиокнопки (radioButton_profile, radioButton_product, radioButton_new)
- `spinBox_context` - Счетчики (spinBox_quantity, spinBox_priority, spinBox_order)
- `progressBar_context` - Индикаторы прогресса (progressBar_loading, progressBar_completion)
- `horizontalSlider_context` - Ползунки (horizontalSlider_priority, horizontalSlider_position)
- `groupBox_context` - Группы (groupBox_details, groupBox_equipment, groupBox_settings)
- `tabWidget_context` - Вкладки (tabWidget_profiles, tabWidget_products, tabWidget_settings)
- `scrollArea_context` - Области прокрутки (scrollArea_content, scrollArea_list, scrollArea_details)
- `frame_context` - Фреймы (frame_header, frame_content, frame_buttons)

**Примеры:**
```
✅ Правильно: pushButton_task_add, label_status, tableWidget_active_tasks
❌ Неправильно: createButton, taskStatusLabel, activeTasksTable
❌ Неправильно: pushButton, label, tableWidget
```

#### 🔧 Работа с UI файлами
**Загрузка UI файлов:**
```python
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile

def load_ui(self):
    ui_file = QFile(UI_PATHS["DIALOG_NAME"])
    ui_file.open(QFile.ReadOnly)
    
    loader = QUiLoader()
    self.ui = loader.load(ui_file)
    ui_file.close()
```

**Доступ к UI элементам:**
```python
# Прямой доступ к элементам через их objectName
self.ui.pushButton_task_save.clicked.connect(self.save_task)
self.ui.tableWidget_tasks.itemSelectionChanged.connect(self.on_selection_changed)
self.ui.label_status.setText("Готово")

# НЕ используйте findChild() - обращайтесь напрямую
# ❌ Неправильно: self.ui.findChild(QPushButton, "pushButton_task_save")
# ✅ Правильно: self.ui.pushButton_task_save
```

**Что должно быть в коде vs UI:**
- ✅ UI файл: Структура виджетов, макеты, базовые свойства, objectName
- ✅ Код: Привязка данных, обработка событий, бизнес-логика, динамический контент
- ❌ UI файл: Динамический контент, сложная логика
- ❌ Код: Создание виджетов, настройка макетов, статическая стилизация

#### 🏠 Паттерн главного окна (обязательный стандарт)
**ЭТАЛОННАЯ структура для всех главных окон (проверено и работает):**
```python
from PySide6.QtWidgets import QMainWindow, QMessageBox
from PySide6.QtCore import QFile
from PySide6.QtUiTools import QUiLoader
from .resources import UI_PATHS

class MainWindow(QMainWindow):
    """Главное окно приложения"""
    
    def __init__(self):
        super().__init__()
        self.load_ui()
        self.setup_ui()

    def load_ui(self):
        """Загрузка UI из файла"""
        ui_file = QFile(UI_PATHS["MAIN_WINDOW"])
        ui_file.open(QFile.ReadOnly)
        
        loader = QUiLoader()
        self.ui = loader.load(ui_file)
        ui_file.close()

        self.setWindowTitle(self.ui.windowTitle())
        self.setGeometry(self.ui.geometry())
        self.setMenuBar(self.ui.menubar)
        self.setStatusBar(self.ui.statusbar)
        self.setCentralWidget(self.ui.centralwidget)

    def setup_ui(self):
        """Настройка UI компонентов после загрузки"""
        self.ui.pushButton_test.clicked.connect(self.on_test_clicked)

    def on_test_clicked(self):
        """Обработка нажатия тестовой кнопки"""
        QMessageBox.information(self, "Тест", "Главное окно работает!")
```

**Принципы этого паттерна:**
- ✅ Максимальная простота - никаких проверок и лишнего кода
- ✅ Прямой доступ к элементам без `findChild()`
- ✅ Один метод `load_ui()` выполняет всю загрузку и настройку
- ✅ Все свойства переносятся из UI файла напрямую
- ❌ НЕ добавляйте `hasattr()`, `if not`, отладочные `print()`
- ❌ НЕ разбивайте на множество методов если код простой

**ВАЖНО:** Этот паттерн проверен и является максимально эффективным. Не усложняйте его!

#### 📣 Сигналы и слоты
- Используйте декораторы `@Slot()` для слотов
- Используйте типизированные сигналы: `Signal(str)` вместо `Signal()`
- Избегайте "магических" подключений типа `connectSlotsByName`
- Подключайте события через `connect` (например, `self.button.clicked.connect(self.on_button_clicked)`)
- Отключайте сигналы при уничтожении объектов
- Избегайте анонимных лямбд где это не нужно

#### 🧰 Использование ресурсов
- Используйте `.qrc` файлы для изображений и других ресурсов
- Импортируйте их через `import qrc_resources` после компиляции

#### Дизайн и стили
- Используйте QSS вместо стилей, заданных в коде
- Создавайте отдельные файлы стилей: `resources/styles/main.qss`, `resources/styles/dialogs.qss`
- Храните пути к файлам в константах: `MAIN_STYLE_PATH = "resources/styles/main.qss"`
- Загружайте стили через `self.setStyleSheet()` используя константы путей
- **ВСЕ ЦВЕТА ДОЛЖНЫ БЫТЬ ОПРЕДЕЛЕНЫ В `constants.py`** в словаре `COLORS`
- **В QSS файлах НЕ используйте прямые значения цветов** - только ссылки на константы
- Используйте префикс `COLOR_` для всех цветовых констант (например, `COLOR_PRIMARY`, `COLOR_BACKGROUND`)
- Обрабатывайте подстановку констант в QSS через `style_utils.py`

**Пример работы с цветами:**
```python
# constants.py
COLORS = {
    "COLOR_PRIMARY": "#2196F3",
    "COLOR_SECONDARY": "#FFC107", 
    "COLOR_SUCCESS": "#4CAF50",
    "COLOR_ERROR": "#F44336",
    "COLOR_BACKGROUND": "#f5f5f5"
}

# В QSS файле используйте плейсхолдеры
# main_template.qss
QPushButton {
    background-color: {{COLOR_PRIMARY}};
    color: white;
}

QMainWindow {
    background-color: {{COLOR_BACKGROUND}};
}

# style_utils.py обрабатывает подстановку
def load_styles_with_constants(qss_file_path):
    with open(qss_file_path, 'r', encoding='utf-8') as file:
        stylesheet = file.read()
    
    # Замена констант из COLORS
    for color_name, color_value in COLORS.items():
        stylesheet = stylesheet.replace(f"{{{{{color_name}}}}}", color_value)
    
    return stylesheet
```

#### 🧑‍💻 Практики ООП
- Все виджеты должны быть частью класса, а не глобальными
- Используйте наследование когда необходимо
- Используйте `super()` для вызова методов родителя
- Предпочитайте композицию наследованию

#### 🧽 Управление памятью Qt
- Qt автоматически управляет памятью через систему родитель-потомок
- Убедитесь что все виджеты добавлены в родительский контейнер или макет
- Избегайте утечек памяти через неправильное использование сигналов/слотов

#### 🧬 Асинхронные операции
- Для длительных операций используйте:
  - `QThread`
  - `QRunnable + QThreadPool`
  - `asyncqt + asyncio` (если применимо)
- Не блокируйте главный поток!

## Критические замечания по реализации

- Оборудование для профилей: хранить как битовые флаги или JSON для 7 стандартных типов
- Позиция задачи: реализовать как целочисленную последовательность, пересчитывать при переупорядочивании
- Фильтрация статусов: использовать параметры запроса, а не отдельные эндпоинты
- Отзывчивость UI: использовать QThread для API вызовов чтобы предотвратить зависание
- Русская локаль: обеспечить правильную UTF-8 кодировку в базе данных и API
