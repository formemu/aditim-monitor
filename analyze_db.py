#!/usr/bin/env python3
"""
Анализ структуры базы данных для унификации названий
"""

import sqlite3

def analyze_database():
    conn = sqlite3.connect('aditim-db.db')
    cursor = conn.cursor()
    
    # Получаем все таблицы
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = cursor.fetchall()
    
    print('=== СТРУКТУРА БАЗЫ ДАННЫХ ===')
    for table in tables:
        table_name = table[0]
        print(f'\n📋 ТАБЛИЦА: {table_name}')
        
        # Получаем колонки таблицы
        cursor.execute(f'PRAGMA table_info({table_name})')
        columns = cursor.fetchall()
        
        for col in columns:
            col_name = col[1]
            col_type = col[2]
            is_pk = " (PK)" if col[5] else ""
            is_not_null = " NOT NULL" if col[3] else ""
            print(f'  • {col_name} - {col_type}{is_pk}{is_not_null}')
        
        # Пробуем показать несколько записей
        try:
            cursor.execute(f'SELECT COUNT(*) FROM {table_name}')
            count = cursor.fetchone()[0]
            print(f'  📊 Записей: {count}')
            
            if count > 0 and count < 20:
                cursor.execute(f'SELECT * FROM {table_name} LIMIT 5')
                rows = cursor.fetchall()
                print(f'  📝 Примеры данных:')
                for row in rows:
                    print(f'    {row}')
        except:
            pass
    
    conn.close()

if __name__ == '__main__':
    analyze_database()
