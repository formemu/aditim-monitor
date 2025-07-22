"""
АНАЛИЗ НАЗВАНИЙ В ПРОЕКТЕ ADITIM MONITOR
=======================================

🎯 ЗОЛОТЫЕ ПРАВИЛА ИМЕНОВАНИЯ:

1. ВСЕ НАЗВАНИЯ ТАБЛИЦ, ПОЛЕЙ И МЕТОДОВ - ТОЛЬКО В ЕДИНСТВЕННОМ ЧИСЛЕ!

2. ПОРЯДОК ИМЕНОВАНИЯ: ОТ ОБЩЕГО К ЧАСТНОМУ!

3. ПРЕФИКСЫ ДЛЯ ТИПОВ СУЩНОСТЕЙ:
   - dir_ для справочников (dir_department, dir_task_status)
   - БЕЗ префикса для основных сущностей (profile, product, task)

4. СУФФИКСЫ ДЛЯ ТИПОВ ДАННЫХ:
   - _id для внешних ключей (department_id, profile_id)
   - _at для временных меток (created_at, updated_at)
   - _on для дат (deadline_on, started_on)

5. ГЛАГОЛЫ В API МЕТОДАХ:
   - get_ для получения данных (get_profile, get_department)
   - create_ для создания (create_profile_tool, create_task)
   - update_ для обновления (update_task_status, update_profile)
   - delete_ для удаления (delete_task, delete_component)

6. API ENDPOINTS БЕЗ ГЛАГОЛОВ:
   - GET /api/profile/ (не /api/get_profiles/)
   - POST /api/profile/ (не /api/create_profile/)
   - PUT /api/profile/{id} (не /api/update_profile/)

7. КОНСТАНТЫ В ВЕРХНЕМ РЕГИСТРЕ СО ЗМЕИНЫМ_СТИЛЕМ:
   - API_BASE_URL, DEFAULT_STATUS_ID, MAX_RETRY_COUNT

8. ФАЙЛЫ И ПАПКИ В НИЖНЕМ РЕГИСТРЕ:
   - api_client.py, main_window.py, profile_tool.py
   - src/client/, src/server/, src/shared/

9. КЛАССЫ В CamelCase:
   - ApiClient, MainWindow, ProfileTool, ReferencesManager

10. ПЕРЕМЕННЫЕ И ФУНКЦИИ В snake_case:
    - current_profile, selected_tool_id, load_component_type()

11. UI ЭЛЕМЕНТЫ С ПРЕФИКСОМ ТИПА:
    - pushButton_task_save, tableWidget_profile, lineEdit_search
    - label_status, comboBox_department, checkBox_urgent

12. СХЕМЫ ВАЛИДАЦИИ С СУФФИКСОМ:
    - ProfileResponse, TaskRequest, ComponentCreate, DepartmentUpdate

13. ИСКЛЮЧЕНИЯ С СУФФИКСОМ Error:
    - ApiConnectionError, ValidationError, DatabaseError

14. ЛОГИЧЕСКИЕ ФЛАГИ С ПРЕФИКСОМ is_/has_/can_:
    - is_active, has_components, can_edit, is_background

15. КОНФИГУРАЦИОННЫЕ ФАЙЛЫ:
    - .yaml для конфигурации, .qss для стилей, .ui для интерфейсов

Примеры правила единственного числа:
✅ dir_department (не departments)
✅ get_department() (не get_departments())  
✅ /api/directory/department (не departments)
✅ product_id (не products_id)

Примеры правила "от общего к частному":
✅ profile_tool_component (профиль -> инструмент -> компонент)
✅ task_component_status (задача -> компонент -> статус)
✅ product_component_type (изделие -> компонент -> тип)
✅ dir_component_status (справочник -> компонент -> статус)

❌ НЕПРАВИЛЬНО: component_profile_tool, status_component_task
❌ НЕПРАВИЛЬНО: tool_profile, type_component

Эти правила действуют даже если логически кажется, что должно быть по-другому.

💡 ПРИМЕРЫ ПРИМЕНЕНИЯ ПРАВИЛ В ПРОЕКТЕ:

ТАБЛИЦЫ БД:
✅ profile, product, task (основные сущности)  
✅ dir_department, dir_task_status (справочники)
✅ profile_tool_component (от общего к частному)

API ENDPOINTS:
✅ GET /api/profile/ (получить все профили)
✅ GET /api/profile/{id} (получить профиль по ID)
✅ POST /api/profile/ (создать профиль)
✅ PUT /api/profile/{id} (обновить профиль)

МЕТОДЫ API КЛИЕНТА:
✅ get_profile(), create_task(), update_component_status()
✅ delete_profile_tool(), search_profile_by_article()

UI ЭЛЕМЕНТЫ:
✅ pushButton_profile_save, tableWidget_task_list
✅ lineEdit_profile_search, comboBox_department_filter

ПЕРЕМЕННЫЕ:
✅ current_profile_id, selected_department_name
✅ is_loading, has_unsaved_change, can_edit_task

ФАЙЛЫ:
✅ profile_tool.py, main_window.py, api_client.py
✅ dialog_create_task.ui, main_template.qss

🔍 ПРОБЛЕМНЫЕ ЗОНЫ В НАЗВАНИЯХ:

1. ДЕПАРТАМЕНТЫ / ОТДЕЛЫ
   📋 БД: dir_departament (ед.ч.) + поле id_departament 
   🔗 API: /api/directories/departments (мн.ч.)
   📡 Client: get_departments() (мн.ч.)
   ⚠️  ПРОБЛЕМА: 'departament' vs 'department' + ед.ч./мн.ч.
   
2. СТАТУСЫ ЗАДАЧ vs СТАТУСЫ КОМПОНЕНТОВ  
   📋 БД: dir_queue_status (статусы задач)
   📋 БД: dir_component_statuses (статусы компонентов)  
   🔗 API: /api/directories/statuses (статусы задач)
   🔗 API: /api/directories/component-statuses (статусы компонентов)
   📡 Client: get_statuses() (статусы задач)
   📡 Client: get_component_statuses() (статусы компонентов) 
   ⚠️  ПРОБЛЕМА: Путаница между статусами задач и компонентов
   
3. РАЗМЕРНОСТИ ИНСТРУМЕНТОВ (ДУБЛИРОВАНИЕ ТАБЛИЦ)
   📋 БД: dir_tool_dimension (пустая)
   📋 БД: dir_tool_dimensions (с данными)
   🔗 API: /api/directories/tool-dimensions
   ⚠️  ПРОБЛЕМА: Две похожие таблицы с одинаковой структурой
   
4. ПРОФИЛИ vs ИЗДЕЛИЯ vs ИНСТРУМЕНТЫ ПРОФИЛЕЙ
   📋 БД: profiles (профили)
   📋 БД: products (изделия) 
   📋 БД: profile_tools (инструменты профилей)
   🔗 API: /api/products/profiles
   🔗 API: /api/products/products  
   🔗 API: /api/products/profile-tools
   ⚠️  ПРОБЛЕМА: Все в одном API разделе "products"
   
5. КОМПОНЕНТЫ (МНОЖЕСТВЕННЫЕ СУЩНОСТИ)
   📋 БД: dir_component (справочник компонентов) - пустая
   📋 БД: dir_component_types (типы компонентов)
   📋 БД: product_components (компоненты изделий) 
   📋 БД: profile_tools_components (компоненты инструментов)
   📋 БД: task_components (компоненты задач)
   🔗 API: /api/directories/components (справочник компонентов)
   🔗 API: /api/directories/component-types (типы компонентов)
   ⚠️  ПРОБЛЕМА: Много разных "компонентов" с разным назначением

📊 АНАЛИЗ КЛЮЧЕВЫХ ПОЛЕЙ:

ВНЕШНИЕ КЛЮЧИ В БД:
- products.id_departament -> dir_departament.id
- task.id_departament -> dir_departament.id  
- task.id_product -> products.id
- task.id_profile -> profiles.id
- task.id_status -> dir_queue_status.id
- profile_tools.profile_id -> profiles.id
- profile_tools.dimension_id -> dir_tool_dimensions.id
- profile_tools_components.tool_id -> profile_tools.id
- profile_tools_components.component_type_id -> dir_component_types.id
- profile_tools_components.status_id -> dir_component_statuses.id

🎯 ПРЕДЛОЖЕНИЯ ПО УНИФИКАЦИИ (С УЧЕТОМ ПРАВИЛА ЕДИНСТВЕННОГО ЧИСЛА):

1. ДЕПАРТАМЕНТЫ:
   ❌ БЫЛО: dir_departament, id_departament, get_departments()  
   ✅ СТАЛО: dir_department, department_id, get_department()
   
2. СТАТУСЫ:
   ❌ БЫЛО: dir_queue_status, dir_component_statuses, get_statuses()
   ✅ СТАЛО: dir_task_status, dir_component_status, get_task_status()
   
3. РАЗМЕРНОСТИ:
   ❌ БЫЛО: dir_tool_dimension + dir_tool_dimensions
   ✅ СТАЛО: dir_tool_dimension (одна таблица)
   
4. ПРОФИЛИ И ИЗДЕЛИЯ:
   ❌ БЫЛО: profiles, products, get_profiles(), get_products()
   ✅ СТАЛО: profile, product, get_profile(), get_product()
   
5. API ГРУППИРОВКА:
   ❌ БЫЛО: Все в /api/products/
   ✅ СТАЛО: 
   - /api/profile/ (профили)
   - /api/product/ (изделия) 
   - /api/tool/ (инструменты профилей)
   - /api/directory/ (справочники)
   
6. ВНЕШНИЕ КЛЮЧИ:
   ❌ БЫЛО: id_departament, id_product, id_profile, id_status
   ✅ СТАЛО: department_id, product_id, profile_id, status_id

7. КОМПОНЕНТЫ (ПРАВИЛО "ОТ ОБЩЕГО К ЧАСТНОМУ"):
   ❌ БЫЛО: dir_component_types, product_components, profile_tools_components
   ✅ СТАЛО: dir_component_type, product_component, profile_tool_component

8. ИНСТРУМЕНТЫ ПРОФИЛЕЙ:
   ❌ БЫЛО: profile_tools (правильный порядок, но множественное число)
   ✅ СТАЛО: profile_tool (единственное число, порядок уже правильный)

9. СВЯЗАННЫЕ ТАБЛИЦЫ (ПРАВИЛО "ОТ ОБЩЕГО К ЧАСТНОМУ"):
   ❌ БЫЛО: task_components -> task_component (порядок правильный)
   ✅ СТАЛО: task_component (без изменений порядка)

🚀 ПЛАН МИГРАЦИИ (ОБНОВЛЕННЫЙ):

ЭТАП 1: База данных
- Переименовать dir_departament -> dir_department (исправление орфографии)
- Переименовать dir_queue_status -> dir_task_status (уточнение назначения)
- Переименовать dir_component_statuses -> dir_component_status (мн.ч. -> ед.ч.)
- Переименовать dir_tool_dimensions -> dir_tool_dimension (мн.ч. -> ед.ч.)
- Переименовать dir_component_types -> dir_component_type (мн.ч. -> ед.ч.)
- Переименовать profiles -> profile (мн.ч. -> ед.ч.)
- Переименовать products -> product (мн.ч. -> ед.ч.)
- Переименовать profile_tools -> profile_tool (мн.ч. -> ед.ч.)
- Переименовать product_components -> product_component (мн.ч. -> ед.ч.)
- Переименовать profile_tools_components -> profile_tool_component (мн.ч. -> ед.ч.)
- Переименовать task_components -> task_component (мн.ч. -> ед.ч.)
- Переименовать все id_* поля в *_id

ЭТАП 2: Модели SQLAlchemy
- Обновить все модели под новые названия таблиц
- Обновить названия полей

ЭТАП 3: API Endpoints
- Реструктурировать API по логическим группам
- Обновить все пути endpoints

ЭТАП 4: Клиент  
- Обновить все методы API клиента
- Обновить ReferencesManager
- Обновить UI компоненты

ЭТАП 5: Тестирование
- Проверить все связи
- Убедиться что миграция прошла успешно
"""
