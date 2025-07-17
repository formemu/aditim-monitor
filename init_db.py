"""
Initialize database with test data for ADITIM Monitor
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from server.database import SessionLocal, engine
from server.models import Base, DirDepartament, DirTypeWork, DirQueueStatus, Profile, Product, Task

# Create tables
Base.metadata.create_all(bind=engine)

def init_db():
    """Initialize database with test data"""
    db = SessionLocal()
    
    try:
        # Check if data already exists
        if db.query(DirDepartament).count() > 0:
            print("Database already initialized")
            return
        
        # Add departments
        departments = [
            DirDepartament(name="Цех металлообработки"),
            DirDepartament(name="Инструментальный цех"), 
            DirDepartament(name="Сборочный цех")
        ]
        for dept in departments:
            db.add(dept)
        
        # Add work types
        work_types = [
            DirTypeWork(name="новый инструмент"),
            DirTypeWork(name="новый вариант"),
            DirTypeWork(name="добавить к существующему"),
            DirTypeWork(name="переделать"),
            DirTypeWork(name="доработка")
        ]
        for wt in work_types:
            db.add(wt)
        
        # Add statuses
        statuses = [
            DirQueueStatus(name="Новая"),
            DirQueueStatus(name="В работе"),
            DirQueueStatus(name="Выполнена"),
            DirQueueStatus(name="Отменена")
        ]
        for status in statuses:
            db.add(status)
        
        db.commit()
        
        # Add test profiles
        profiles = [
            Profile(article="П-001", sketch="Профиль для плит"),
            Profile(article="П-002", sketch="Профиль для пальцев"),
            Profile(article="П-003", sketch="Профиль для усреднителя")
        ]
        for profile in profiles:
            db.add(profile)
        
        # Add test products
        products = [
            Product(name="Деталь А", id_departament=1, sketch="Эскиз детали А"),
            Product(name="Деталь Б", id_departament=1, sketch="Эскиз детали Б"),
            Product(name="Корпус", id_departament=2, sketch="Эскиз корпуса")
        ]
        for product in products:
            db.add(product)
        
        db.commit()
        
        # Add test tasks
        tasks = [
            Task(
                id_profile=1,
                id_departament=1,
                equipment="плиты 1",
                deadline="2025-01-25",
                position=1,
                id_type_work=1,
                id_status=1
            ),
            Task(
                id_profile=2,
                id_departament=1,
                equipment="пальцы",
                deadline="2025-01-30",
                position=2,
                id_type_work=2,
                id_status=2
            ),
            Task(
                id_product=1,
                id_departament=2,
                equipment="станок ЧПУ",
                deadline="2025-02-05",
                position=3,
                id_type_work=1,
                id_status=1
            )
        ]
        for task in tasks:
            db.add(task)
        
        db.commit()
        print("Database initialized with test data")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
