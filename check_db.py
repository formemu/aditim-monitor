import sqlite3
conn = sqlite3.connect('queue.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in cursor.fetchall()]
print("Database tables:", tables)

if 'tasks' in tables:
    cursor.execute("SELECT COUNT(*) FROM tasks")
    count = cursor.fetchone()[0]
    print(f"Tasks count: {count}")

conn.close()
