"""
Скрипт миграции базы данных для унификации названий
"""

import sqlite3
import shutil
from datetime import datetime

def backup_database():
    """Создаем резервную копию базы данных"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"aditim-db_backup_{timestamp}.db"
    shutil.copy2("aditim-db.db", backup_name)
    print(f"✅ Создан бэкап: {backup_name}")
    return backup_name

def migrate_database():
    """Выполняет миграцию базы данных"""
    print("🚀 Начинаем миграцию базы данных...")
    
    # Создаем бэкап
    backup_file = backup_database()
    
    try:
        conn = sqlite3.connect('aditim-db.db')
        cursor = conn.cursor()
        
        print("\n📋 ЭТАП 1: Переименование таблиц (ПРАВИЛО: ЕДИНСТВЕННОЕ ЧИСЛО)...")
        
        # 1. Исправляем орфографию: dir_departament -> dir_department  
        print("  • Исправление орфографии: dir_departament -> dir_department")
        cursor.execute("ALTER TABLE dir_departament RENAME TO dir_department")
        
        # 2. Уточняем назначение: dir_queue_status -> dir_task_status
        print("  • Уточнение назначения: dir_queue_status -> dir_task_status")
        cursor.execute("ALTER TABLE dir_queue_status RENAME TO dir_task_status")
        
        # 3. Множественное -> единственное число для справочников
        print("  • Мн.ч. -> ед.ч.: dir_component_statuses -> dir_component_status")
        cursor.execute("ALTER TABLE dir_component_statuses RENAME TO dir_component_status")
        
        print("  • Мн.ч. -> ед.ч.: dir_tool_dimensions -> dir_tool_dimension")
        cursor.execute("ALTER TABLE dir_tool_dimensions RENAME TO dir_tool_dimension")
        
        print("  • Мн.ч. -> ед.ч.: dir_component_types -> dir_component_type")
        cursor.execute("ALTER TABLE dir_component_types RENAME TO dir_component_type")
        
        # 4. Множественное -> единственное число для основных таблиц
        print("  • Мн.ч. -> ед.ч.: profiles -> profile")
        cursor.execute("ALTER TABLE profiles RENAME TO profile")
        
        print("  • Мн.ч. -> ед.ч.: products -> product")
        cursor.execute("ALTER TABLE products RENAME TO product")
        
        print("  • Мн.ч. -> ед.ч.: profile_tools -> profile_tool")
        cursor.execute("ALTER TABLE profile_tools RENAME TO profile_tool")
        
        print("  • Мн.ч. -> ед.ч.: product_components -> product_component")
        cursor.execute("ALTER TABLE product_components RENAME TO product_component")
        
        print("  • Мн.ч. -> ед.ч.: profile_tools_components -> profile_tool_component")
        cursor.execute("ALTER TABLE profile_tools_components RENAME TO profile_tool_component")
        
        print("  • Мн.ч. -> ед.ч.: task_components -> task_component")
        cursor.execute("ALTER TABLE task_components RENAME TO task_component")
        
        # 5. Удаляем дублирующие таблицы если есть
        print("  • Проверка и удаление дублирующих таблиц")
        cursor.execute("DROP TABLE IF EXISTS dir_tool_dimensions")  # на случай если останется дубль
        
        print("\n📋 ЭТАП 2: Обновление внешних ключей (id_* -> *_id)...")
        
        # Обновляем поля в product (бывшей products)
        print("  • product: id_departament -> department_id")
        cursor.execute("ALTER TABLE product RENAME COLUMN id_departament TO department_id")
        
        # Обновляем поля в task  
        print("  • task: id_departament -> department_id")
        cursor.execute("ALTER TABLE task RENAME COLUMN id_departament TO department_id")
        
        print("  • task: id_product -> product_id") 
        cursor.execute("ALTER TABLE task RENAME COLUMN id_product TO product_id")
        
        print("  • task: id_profile -> profile_id")
        cursor.execute("ALTER TABLE task RENAME COLUMN id_profile TO profile_id")
        
        print("  • task: id_status -> status_id")
        cursor.execute("ALTER TABLE task RENAME COLUMN id_status TO status_id")
        
        print("\n📋 ЭТАП 3: Обновление архитектуры (Task -> ProfileTool вместо Profile)...")
        
        print("  • task: profile_id -> profile_tool_id")
        cursor.execute("ALTER TABLE task RENAME COLUMN profile_id TO profile_tool_id")
        
        conn.commit()
        print("\n✅ Миграция базы данных завершена успешно!")
        
        # Проверяем результат
        print("\n🔍 Проверка результатов миграции:")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = cursor.fetchall()
        for table in tables:
            print(f"  ✓ {table[0]}")
            
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Ошибка миграции: {e}")
        print(f"🔄 Восстанавливаем из бэкапа {backup_file}")
        shutil.copy2(backup_file, "aditim-db.db")
        return False

if __name__ == '__main__':
    success = migrate_database()
    if success:
        print("\n🎉 Миграция завершена! Можно продолжать обновление кода.")
    else:
        print("\n💥 Миграция провалилась! База данных восстановлена из бэкапа.")
