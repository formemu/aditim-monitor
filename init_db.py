"""
Initialize database with test data for ADITIM Monitor
"""

import sys
from pathlib import Path
from datetime import date
sys.path.insert(0, str(Path(__file__).parent / "src"))

from server.database import SessionLocal, engine, Base
from server.models.directories import DirDepartament, DirTypeWork, DirQueueStatus
from server.models.products import Profile, Product
from server.models.profile_tools import (
    ToolDimension, ComponentType, ComponentStatus, 
    ProfileTool, ProfileToolComponent, ProductComponent
)
from server.models.tasks import Task

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
        
        # Add tool dimensions
        tool_dimensions = [
            ToolDimension(dimension="250x190(250x130)", description="Стандартная размерность для средних профилей"),
            ToolDimension(dimension="300x200(300x150)", description="Большая размерность для крупных профилей"),
            ToolDimension(dimension="200x150(200x100)", description="Малая размерность для небольших профилей")
        ]
        for dim in tool_dimensions:
            db.add(dim)
        
        # Add component types
        component_types = [
            ComponentType(name="плита_1", description="Первая плита"),
            ComponentType(name="плита_2", description="Вторая плита"),
            ComponentType(name="плита_3", description="Третья плита"),
            ComponentType(name="плита_4", description="Четвертая плита"),
            ComponentType(name="пальцы", description="Пальцы"),
            ComponentType(name="усреднитель", description="Усреднитель"),
            ComponentType(name="кондуктор", description="Кондуктор")
        ]
        for comp_type in component_types:
            db.add(comp_type)
        
        # Add component statuses
        component_statuses = [
            ComponentStatus(name="в разработке", description="Компонент находится в стадии разработки"),
            ComponentStatus(name="изготовление", description="Компонент изготавливается"),
            ComponentStatus(name="на испытаниях", description="Компонент проходит испытания"),
            ComponentStatus(name="в работе", description="Компонент используется в производстве"),
            ComponentStatus(name="не пошел", description="Компонент не прошел испытания"),
            ComponentStatus(name="брак", description="Компонент забракован")
        ]
        for comp_status in component_statuses:
            db.add(comp_status)
        
        db.commit()
        
        # Add test profiles
        profiles = [
            Profile(article="П-001", description="Профиль для оконных рам"),
            Profile(article="П-002", description="Профиль для дверных коробок"),
            Profile(article="П-003", description="Профиль для вентиляционных решеток")
        ]
        for profile in profiles:
            db.add(profile)
        
        # Add test products
        products = [
            Product(name="Деталь А", article="ДТ-001", description="Металлическая деталь для станка", id_departament=1),
            Product(name="Корпус", article="КР-002", description="Корпус электрического шкафа", id_departament=2),
            Product(name="Фланец", article="ФЛ-003", description="Соединительный фланец", id_departament=1)
        ]
        for product in products:
            db.add(product)
        
        db.commit()
        
        # Add test profile tools
        profile_tools = [
            ProfileTool(profile_id=1, dimension_id=1, description="Инструмент для профиля П-001"),
            ProfileTool(profile_id=2, dimension_id=2, description="Инструмент для профиля П-002"),
            ProfileTool(profile_id=3, dimension_id=1, description="Инструмент для профиля П-003")
        ]
        for tool in profile_tools:
            db.add(tool)
        
        db.commit()
        
        # Add test profile tool components
        tool_components = [
            # Компоненты для первого инструмента
            ProfileToolComponent(tool_id=1, component_type_id=1, variant=1, description="Плита 1 для инструмента П-001", status_id=4),
            ProfileToolComponent(tool_id=1, component_type_id=2, variant=1, description="Плита 2 для инструмента П-001", status_id=4),
            ProfileToolComponent(tool_id=1, component_type_id=5, variant=1, description="Пальцы для инструмента П-001", status_id=3),
            
            # Компоненты для второго инструмента
            ProfileToolComponent(tool_id=2, component_type_id=1, variant=1, description="Плита 1 для инструмента П-002", status_id=2),
            ProfileToolComponent(tool_id=2, component_type_id=3, variant=2, description="Плита 3 вариант 2 для инструмента П-002", status_id=1),
        ]
        for component in tool_components:
            db.add(component)
        
        # Add test product components
        product_components = [
            ProductComponent(product_id=1, component_name="Болт М10", description="Крепежный болт", quantity=4),
            ProductComponent(product_id=1, component_name="Шайба", description="Плоская шайба", quantity=4),
            ProductComponent(product_id=2, component_name="Дверца", description="Передняя дверца", quantity=1),
            ProductComponent(product_id=2, component_name="Петля", description="Петля для дверцы", quantity=2),
        ]
        for comp in product_components:
            db.add(comp)
        
        db.commit()
        
        # Add test tasks
        tasks = [
            Task(
                id_profile=1,
                id_departament=1,
                equipment="плиты 1",
                deadline=date(2025, 1, 25),
                position=1,
                id_type_work=1,
                id_status=1
            ),
            Task(
                id_profile=2,
                id_departament=1,
                equipment="пальцы",
                deadline=date(2025, 1, 30),
                position=2,
                id_type_work=2,
                id_status=2
            ),
            Task(
                id_product=1,
                id_departament=2,
                equipment="станок ЧПУ",
                deadline=date(2025, 2, 5),
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
