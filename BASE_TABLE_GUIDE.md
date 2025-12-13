# 📋 БАЗОВЫЙ КЛАСС ДЛЯ ТАБЛИЦ - ИНСТРУКЦИЯ ПО ИСПОЛЬЗОВАНИЮ

## 🎯 НАЗНАЧЕНИЕ

`BaseTable` — статический класс-утилита для унификации работы с `QTableWidget`.

Решает проблемы:
- ❌ Дублирование кода `setRowCount`, `setColumnCount`, `setHorizontalHeaderLabels`
- ❌ Повторяющаяся логика создания `QTableWidgetItem`
- ❌ Разрозненные способы установки `UserRole` данных
- ❌ Ручное заполнение таблиц в цикле

## 🔧 ОСНОВНЫЕ МЕТОДЫ

### 1. `setup_table()` — Настройка структуры таблицы

**До:**
```python
table = self.ui.tableWidget_profile
table.setColumnCount(2)
table.setHorizontalHeaderLabels(["Артикул", "Описание"])
table.setRowCount(len(api_manager.table["profile"]))
table.horizontalHeader().setStretchLastSection(True)
```

**После:**
```python
from ..base_table import BaseTable

BaseTable.setup_table(
    self.ui.tableWidget_profile,
    ["Артикул", "Описание"],
    count_row=len(api_manager.table["profile"])
)
```

**Экономия: 4 строки → 1 строка**

---

### 2. `populate_row()` — Заполнение одной строки

**До:**
```python
item_article = QTableWidgetItem(profile['article'])
item_description = QTableWidgetItem(profile['description'])

item_article.setData(Qt.UserRole, profile['id'])
item_description.setData(Qt.UserRole, profile['id'])

table.setItem(row, 0, item_article)
table.setItem(row, 1, item_description)
```

**После:**
```python
BaseTable.populate_row(
    table,
    row,
    [profile['article'], profile['description']],
    data_id=profile['id']
)
```

**Экономия: 7 строк → 1 строка**

---

### 3. `populate_table()` — Полное заполнение таблицы

**До (window_profile.py):**
```python
def update_profile_table(self):
    """Обновление таблицы профилей"""
    table = self.ui.tableWidget_profile
    table.setRowCount(len(api_manager.table["profile"]))
    table.setColumnCount(2)
    table.setHorizontalHeaderLabels(["Артикул", "Описание"])
    table.horizontalHeader().setStretchLastSection(True)

    for row, profile in enumerate(api_manager.table["profile"]):
        item_article = QTableWidgetItem(profile['article'])
        item_description = QTableWidgetItem(profile['description'])

        item_article.setData(Qt.UserRole, profile['id'])
        item_description.setData(Qt.UserRole, profile['id'])

        table.setItem(row, 0, item_article)
        table.setItem(row, 1, item_description)
```
**18 строк**

**После:**
```python
def update_profile_table(self):
    """Обновление таблицы профилей"""
    BaseTable.populate_table(
        self.ui.tableWidget_profile,
        ["Артикул", "Описание"],
        api_manager.table["profile"],
        func_row_mapper=lambda p: [p['article'], p['description']],
        func_id_getter=lambda p: p['id']
    )
```
**10 строк**

**Экономия: 18 строк → 10 строк (-44%)**

---

### 4. `clear_table()` — Очистка таблицы

**До:**
```python
self.ui.tableWidget_component.setRowCount(0)
self.ui.tableWidget_component_stage.setRowCount(0)
```

**После:**
```python
BaseTable.clear_table(self.ui.tableWidget_component)
BaseTable.clear_table(self.ui.tableWidget_component_stage)
```

**Улучшение: явная семантика, переиспользуемый метод**

---

### 5. `get_selected_id()` — Получение ID выбранной строки

**До:**
```python
def on_profile_table_clicked(self):
    """Обработчик клика по таблице профилей"""
    profile_id = self.ui.tableWidget_profile.currentItem().data(Qt.UserRole)
    # ... использование profile_id
```

**После:**
```python
def on_profile_table_clicked(self):
    """Обработчик клика по таблице профилей"""
    profile_id = BaseTable.get_selected_id(self.ui.tableWidget_profile)
    if profile_id is None:
        return  # Ничего не выбрано
    # ... использование profile_id
```

**Улучшение: безопасная обработка None, явная семантика**

---

### 6. `set_cell_value()` — Установка значения в ячейку

**До:**
```python
item = QTableWidgetItem("Новое значение")
item.setData(Qt.UserRole, some_id)
table.setItem(row, col, item)
```

**После:**
```python
BaseTable.set_cell_value(
    table, row, col,
    "Новое значение",
    data_id=some_id
)
```

**Экономия: 3 строки → 1 строка**

---

## 📊 ПРИМЕРЫ МИГРАЦИИ

### Пример 1: Простая таблица (window_profile.py)

**До (18 строк):**
```python
def update_profile_table(self):
    """Обновление таблицы профилей"""
    table = self.ui.tableWidget_profile
    table.setRowCount(len(api_manager.table["profile"]))
    table.setColumnCount(2)
    table.setHorizontalHeaderLabels(["Артикул", "Описание"])
    table.horizontalHeader().setStretchLastSection(True)

    for row, profile in enumerate(api_manager.table["profile"]):
        item_article = QTableWidgetItem(profile['article'])
        item_description = QTableWidgetItem(profile['description'])

        item_article.setData(Qt.UserRole, profile['id'])
        item_description.setData(Qt.UserRole, profile['id'])

        table.setItem(row, 0, item_article)
        table.setItem(row, 1, item_description)
```

**После (10 строк):**
```python
def update_profile_table(self):
    """Обновление таблицы профилей"""
    BaseTable.populate_table(
        self.ui.tableWidget_profile,
        ["Артикул", "Описание"],
        api_manager.table["profile"],
        func_row_mapper=lambda p: [p['article'], p['description']],
        func_id_getter=lambda p: p['id']
    )
```

---

### Пример 2: Таблица с вложенными данными (window_product.py)

**До (16 строк):**
```python
def update_table_product(self):
    """Обновление таблицы изделий"""
    table = self.ui.tableWidget_product
    table.setRowCount(len(api_manager.table['product']))
    table.setColumnCount(3)
    table.setHorizontalHeaderLabels(["Название", "Департамент", "Описание"])
    table.horizontalHeader().setStretchLastSection(True)
    
    for row, product in enumerate(api_manager.table['product']):
        item_name = QTableWidgetItem(product['name'])
        item_department = QTableWidgetItem(product['department']['name'])
        item_description = QTableWidgetItem(product['description'])

        item_name.setData(Qt.UserRole, product['id'])
        item_department.setData(Qt.UserRole, product['id'])
        item_description.setData(Qt.UserRole, product['id'])

        table.setItem(row, 0, item_name)
        table.setItem(row, 1, item_department)
        table.setItem(row, 2, item_description)
```

**После (11 строк):**
```python
def update_table_product(self):
    """Обновление таблицы изделий"""
    BaseTable.populate_table(
        self.ui.tableWidget_product,
        ["Название", "Департамент", "Описание"],
        api_manager.table['product'],
        func_row_mapper=lambda p: [
            p['name'],
            p['department']['name'],
            p['description']
        ],
        func_id_getter=lambda p: p['id']
    )
```

---

### Пример 3: Таблица из справочника (window_setting.py)

**До (14 строк):**
```python
def update_table_dimension(self):
    """Обновление таблицы размерностей"""
    table = self.ui.tableWidget_dimension
    list_dimension = api_manager.directory.get('profiletool_dimension', [])
    table.setRowCount(len(list_dimension))
    table.setColumnCount(2)
    table.setHorizontalHeaderLabels(["Название", "Описание"])
    table.horizontalHeader().setStretchLastSection(True)

    for row, dimension in enumerate(list_dimension):
        item_name = QTableWidgetItem(dimension['name'])
        item_description = QTableWidgetItem(dimension.get('description', ''))

        item_name.setData(Qt.UserRole, dimension['id'])
        item_description.setData(Qt.UserRole, dimension['id'])

        table.setItem(row, 0, item_name)
        table.setItem(row, 1, item_description)
```

**После (11 строк):**
```python
def update_table_dimension(self):
    """Обновление таблицы размерностей"""
    list_dimension = api_manager.directory.get('profiletool_dimension', [])
    
    BaseTable.populate_table(
        self.ui.tableWidget_dimension,
        ["Название", "Описание"],
        list_dimension,
        func_row_mapper=lambda d: [d['name'], d.get('description', '')],
        func_id_getter=lambda d: d['id']
    )
```

---

### Пример 4: Сложная таблица с условной логикой (window_product.py)

**До (сложная логика):**
```python
def update_profiletool_component_table(self):
    """Обновление таблицы компонентов инструмента профиля"""
    table = self.ui.tableWidget_component
    table.setRowCount(0)
    table.setColumnCount(4)
    table.setHorizontalHeaderLabels(["Название", "Статус", "Вариант", "Описание"])
    table.setRowCount(len(self.profiletool['component']))
    table.horizontalHeader().setStretchLastSection(True)

    for row, component in enumerate(self.profiletool['component']):
        name_item = QTableWidgetItem(component["type"]["name"])
        
        if component.get("status"):
            status_name = component["status"]["name"]
            status_item = QTableWidgetItem(status_name)
        else:
            status_item = QTableWidgetItem("Новая")
        
        variant_item = QTableWidgetItem(str(component["variant"]))
        
        description_text = component.get("description", "")
        description_item = QTableWidgetItem(description_text)
        
        # ... установка в таблицу
```

**После (разделение логики):**
```python
def update_profiletool_component_table(self):
    """Обновление таблицы компонентов инструмента профиля"""
    
    def map_component_row(component: dict) -> list:
        status_name = component["status"]["name"] if component.get("status") else "Новая"
        return [
            component["type"]["name"],
            status_name,
            str(component["variant"]),
            component.get("description", "")
        ]
    
    BaseTable.populate_table(
        self.ui.tableWidget_component,
        ["Название", "Статус", "Вариант", "Описание"],
        self.profiletool['component'],
        func_row_mapper=map_component_row,
        func_id_getter=lambda c: c['id']
    )
```

**Улучшение: разделение бизнес-логики и отображения**

---

## ⚙️ РАСШИРЕННЫЕ СЦЕНАРИИ

### Ручное заполнение (когда `populate_table` не подходит)

Если таблица сложная (разные UserRole, цвета, стили), используйте комбинацию методов:

```python
def update_complex_table(self):
    """Сложная таблица с кастомизацией"""
    table = self.ui.tableWidget_complex
    list_data = api_manager.table["some_data"]
    
    # Настройка структуры
    BaseTable.setup_table(
        table,
        ["Колонка 1", "Колонка 2", "Колонка 3"],
        count_row=len(list_data)
    )
    
    # Ручное заполнение с кастомизацией
    for row, data in enumerate(list_data):
        # Используем populate_row для базового заполнения
        BaseTable.populate_row(
            table, row,
            [data['field1'], data['field2'], data['field3']],
            data_id=data['id']
        )
        
        # Дополнительная кастомизация
        item = table.item(row, 1)
        item.setBackground(QColor("#FF0000"))  # Красный фон
```

---

### Очистка перед обновлением

```python
def refresh_data(self):
    """Обновление данных с очисткой"""
    # Очистка всех таблиц
    BaseTable.clear_table(self.ui.tableWidget_profile)
    BaseTable.clear_table(self.ui.tableWidget_product)
    
    # Заполнение заново
    self.update_profile_table()
    self.update_product_table()
```

---

## 📈 ОЖИДАЕМАЯ ЭКОНОМИЯ

### По файлам:

| Файл | Таблиц | Строк до | Строк после | Экономия |
|------|--------|----------|-------------|----------|
| window_profile.py | 1 | 18 | 10 | -8 (-44%) |
| window_product.py | 4 | ~70 | ~45 | -25 (-36%) |
| window_setting.py | 3 | ~50 | ~35 | -15 (-30%) |
| window_task.py | 5 | ~90 | ~60 | -30 (-33%) |
| window_blank.py | 2 | ~40 | ~25 | -15 (-38%) |
| window_development.py | 2 | ~35 | ~25 | -10 (-29%) |

**ВСЕГО: ~100-130 строк экономии** (около 25-35% кода таблиц)

---

## ✅ ЧЕКЛИСТ МИГРАЦИИ

### Для каждого метода `update_*_table()`:

1. ✅ Добавить импорт: `from ..base_table import BaseTable`
2. ✅ Заменить настройку таблицы на `BaseTable.setup_table()` или `BaseTable.populate_table()`
3. ✅ Создать `func_row_mapper` lambda или функцию для преобразования данных
4. ✅ Создать `func_id_getter` lambda для получения ID
5. ✅ Удалить старый код создания `QTableWidgetItem`
6. ✅ Протестировать отображение таблицы

### Для обработчиков кликов:

1. ✅ Заменить `table.currentItem().data(Qt.UserRole)` на `BaseTable.get_selected_id(table)`
2. ✅ Добавить проверку `if id is None: return`

---

## 🎯 ПРИОРИТЕТ МИГРАЦИИ

1. **Высокий приоритет** — простые таблицы (profile, dimension, product):
   - Быстрая миграция (5-10 минут на файл)
   - Максимальная экономия (40-50% кода)
   - Минимальный риск

2. **Средний приоритет** — средней сложности таблицы (task, setting):
   - Умеренная миграция (10-15 минут на файл)
   - Хорошая экономия (30-40% кода)
   - Требуется тестирование логики

3. **Низкий приоритет** — сложные таблицы (blank с группировкой):
   - Сложная миграция (15-20 минут на файл)
   - Меньшая экономия (20-30% кода)
   - Требуется детальное тестирование

---

**🎯 ИТОГО: BaseTable сэкономит ~100-130 строк кода и унифицирует работу с таблицами в 7 файлах!**
