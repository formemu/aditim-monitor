<!-- Используйте этот файл для предоставления пользовательских инструкций для Copilot, специфичных для рабочей области. -->

# ADITIM Monitor — Инструкции для AI-агентов

## 🤖 ЗОЛОТЫЕ ПРАВИЛА (TL;DR)

**ОБЯЗАТЕЛЬНО СОБЛЮДАТЬ ВСЕ ПУНКТЫ БЕЗ ИСКЛЮЧЕНИЙ!**

1. **Единственное число** — все сущности, методы, переменные, endpoints
2. **Порядок "тип → содержимое"** — `list_tool` (не `tool_list`), `count_deleted` (не `deleted_count`)
3. **От общего к частному** — `profile_tool_component`, `task_component_status`
4. **Стандартные префиксы/суффиксы** — `dir_`, `_id`, `_at`, `_on`
5. **UI-FIRST** — только .ui файлы, никакого программного создания виджетов
6. **Прямой доступ** — `self.ui.pushButton_save` (не `findChild`)
7. **Константы цветов** — только из `COLORS` словаря
8. **Делать только то, что просит пользователь** — не предлагать и не реализовывать непрошеные изменения

---

# 🎯 ПРАВИЛА ИМЕНОВАНИЯ

## 🔤 1. ЕДИНСТВЕННОЕ ЧИСЛО
**ВСЕ названия - ТОЛЬКО в единственном числе!**
- ✅ `profile`, `get_department()`, `/api/profile/`
- ❌ `profiles`, `get_departments()`, `/api/profiles/`

## 📊 2. ПОРЯДОК "ТИП → СОДЕРЖИМОЕ" 
**Сначала тип данных, потом что за данные**
- ✅ `list_tool`, `count_deleted`, `array_component`
- ❌ `tool_list`, `deleted_count`, `component_array`

## 🏗️ 3. ОТ ОБЩЕГО К ЧАСТНОМУ
**Порядок слов в составных названиях: от общего к частному**
- ✅ `profile_tool_component` (профиль → инструмент → компонент)
- ✅ `task_component_status` (задача → компонент → статус)
- ❌ `component_profile_tool`, `status_component_task`

## 🏷️ 4. ПРЕФИКСЫ И СУФФИКСЫ
**Строго по типу сущности:**
- `dir_` — только справочники (`dir_department`, `dir_task_status`)
- Без префикса — основные сущности (`profile`, `product`, `task`)
- `_id` — внешние ключи (`department_id`, `profile_id`)
- `_at` — временные метки (`created_at`, `updated_at`)
- `_on` — даты (`deadline_on`, `started_on`)

## 🔧 5. ЛОГИЧЕСКИЕ ФЛАГИ
**Только с префиксами:**
- ✅ `is_active`, `has_components`, `can_edit`
- ❌ `active`, `components`, `editable`

---

# 🗂️ АРХИТЕКТУРА ПРОЕКТА

## � База данных
- **12 таблиц** с правильными именами
- **Справочники**: `dir_department`, `dir_task_status`, `dir_component_type`
- **Основные**: `profile`, `product`, `task`, `profile_tool`
- **Связи**: все relationships в единственном числе

## 🔗 API Server
- **Endpoints**: `/api/directories/task-statuses`, `/api/profile-tools`
- **Методы**: `get_`, `create_`, `update_`, `delete_`
- **Схемы**: `ProfileResponse`, `TaskRequest`, `ComponentCreate`

## 💻 Client
- **API клиент**: обновленные endpoints
- **References manager**: метод `get_profile(profile_id)`
- **UI диалоги**: корректная загрузка данных

---

# 🎨 UI/UX ПРАВИЛА

## 🏗️ UI-FIRST Подход
**ВСЕ элементы UI создаются ТОЛЬКО в .ui файлах!**
- ✅ Qt Designer для всех виджетов и макетов
- ✅ Код только для бизнес-логики и обработки событий
- ❌ Программное создание виджетов (QPushButton, QLabel и т.д.)

## 🏷️ Именование UI элементов
**Паттерн: `widgetType_context[_action]`**
- `pushButton_task_save`, `tableWidget_profiles`, `lineEdit_search`
- `label_status`, `comboBox_department`, `checkBox_urgent`

## 🔌 Доступ к элементам
**Только прямой доступ через objectName:**
- ✅ `self.ui.pushButton_save.clicked.connect(self.save_task)`
- ❌ `self.ui.findChild(QPushButton, "pushButton_save")`

## 🎨 Стили и цвета
**ВСЕ цвета только из констант:**
```python
# constants.py
COLORS = {
    "COLOR_PRIMARY": "#2196F3",
    "COLOR_SUCCESS": "#4CAF50",
    "COLOR_ERROR": "#F44336"
}

# В QSS используйте плейсхолдеры
QPushButton { background-color: {{COLOR_PRIMARY}}; }
```

---

# 💻 СТИЛЬ КОДА

## 🐍 Python Стандарты
- **Регистры**: `snake_case` функции, `CamelCase` классы, `UPPER_SNAKE_CASE` константы
- **Длина строки**: максимум 79 символов
- **Пустые строки**: 1 между методами, 2 между классами
- **Обязательно**: docstring и аннотации типов
- **Инструменты**: black, flake8, mypy

## 🏗️ Принципы дизайна
- **SOLID**: разделение ответственности
- **DRY**: не дублировать логику
- **KISS**: простота превыше всего

## 📦 PySide6 Паттерны
**Импорты:**
```python
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import QApplication, QWidget
```

**Загрузка UI:**
```python
def load_ui(self):
    ui_file = QFile(UI_PATHS["MAIN_WINDOW"])
    ui_file.open(QFile.ReadOnly)
    
    loader = QUiLoader()
    self.ui = loader.load(ui_file)
    ui_file.close()
```

**Сигналы и слоты:**
- Декораторы `@Slot()` для слотов
- Типизированные сигналы `Signal(str)`
- Явные `connect()` без "магических" подключений

---

# ⚠️ КРИТИЧЕСКИЕ ТРЕБОВАНИЯ

## 🚫 ЗАПРЕЩЕНО
- Создавать UI элементы программно
- Использовать `findChild()` для доступа к элементам
- Прямые значения цветов в коде/QSS
- Множественное число в именах
- Порядок "содержимое → тип" в переменных
- Нереализованные предложения улучшений

## ✅ ОБЯЗАТЕЛЬНО
- Все UI только через .ui файлы
- Прямой доступ к элементам через objectName
- Цвета только через COLORS константы
- Единственное число во всех именах
- Порядок "тип → содержимое" в переменных
- Делать только то, что просит пользователь

## 🎯 СТАТУС ПРОЕКТА
**По состоянию на 23 июля 2025 г. - УНИФИКАЦИЯ ЗАВЕРШЕНА!**
- ✅ База данных: 100% унифицирована
- ✅ API Server: 100% унифицирован  
- ✅ Client: 100% унифицирован
- ✅ Новое правило "тип → содержимое" внедрено

---

**🤖 ПОМНИ: Ты делаешь только то, что явно просит пользователь. Никаких непрошеных улучшений!**
