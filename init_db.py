"""
Initialize database with test data for ADITIM Monitor
"""

import sys
from pathlib import Path
from datetime import date
sys.path.insert(0, str(Path(__file__).parent / "src"))

from server.database import SessionLocal, engine, Base
from server.models.directories import DirDepartment, DirTaskStatus, DirToolDimension, DirComponentType, DirComponentStatus
from server.models.products import Product, ProductComponent
from server.models.profiles import Profile
from server.models.profile_tools import ProfileTool, ProfileToolComponent
from server.models.tasks import Task, TaskComponent

# Create tables
Base.metadata.create_all(bind=engine)

def init_db():
    """Initialize database with test data"""
    db = SessionLocal()
    
    try:
        # Check if data already exists
        if db.query(DirDepartment).count() > 0:
            print("Database already initialized")
            return
        
        # Add departments
        departments = [
            DirDepartment(name="Цех металлообработки"),
            DirDepartment(name="Цех экструзии"), 
            DirDepartment(name="Лаборатория")
        ]
        for dept in departments:
            db.add(dept)
        
        # Add statuses
        statuses = [
            DirTaskStatus(name="Новая"),
            DirTaskStatus(name="В работе"),
            DirTaskStatus(name="Выполнена"),
            DirTaskStatus(name="Отменена")
        ]
        for status in statuses:
            db.add(status)
        
        # Add tool dimensions
        tool_dimensions = [
            DirToolDimension(name="250x190(250x130)", description="250x190x45 (2 плиты) 250x190x48 (1 плита) 250x130x56 (1 плита)")
        ]
        for dim in tool_dimensions:
            db.add(dim)
        
        # Add component types
        component_types = [
            DirComponentType(name="плита 1", description="Первая плита"),
            DirComponentType(name="плита 2", description="Вторая плита"),
            DirComponentType(name="плита 3", description="Третья плита"),
            DirComponentType(name="плита 4", description="Четвертая плита"),
            DirComponentType(name="пальцы", description="Пальцы"),
            DirComponentType(name="усреднитель", description="Усреднитель"),
            DirComponentType(name="кондуктор", description="Кондуктор")
        ]
        for comp_type in component_types:
            db.add(comp_type)
        
        # Add component statuses
        component_statuses = [
            DirComponentStatus(name="в разработке", description="Компонент находится в стадии разработки"),
            DirComponentStatus(name="изготовление", description="Компонент изготавливается"),
            DirComponentStatus(name="на испытаниях", description="Компонент проходит испытания"),
            DirComponentStatus(name="в работе", description="Компонент используется в производстве"),
            DirComponentStatus(name="не пошел", description="Компонент не прошел испытания"),
            DirComponentStatus(name="брак", description="Компонент забракован")
        ]
        for comp_status in component_statuses:
            db.add(comp_status)
        
        db.commit()
        
        # Add test profiles
        profiles = [
            Profile(article="1634447.1", description="Профиль для оконных рам"),
            Profile(article="1540096.0", description="Профиль для дверных коробок"),
            Profile(article="1641645", description="Профиль для вентиляционных решеток")
        ]
        for profile in profiles:
            db.add(profile)
        
        # Add test products
        products = [
            Product(name="Фланец", description="Соединительный фланец", department_id=1)
        ]
        for product in products:
            db.add(product)
        
        db.commit()
        
        # Add test profile tools
        profile_tools = [
            ProfileTool(profile_id=1, dimension_id=1, description="Инструмент для профиля 1634447.1"),
            ProfileTool(profile_id=2, dimension_id=1, description="Инструмент для профиля 1540096.0"),
            ProfileTool(profile_id=3, dimension_id=1, description="Инструмент для профиля 1641645")
        ]
        for tool in profile_tools:
            db.add(tool)
        
        db.commit()
        
        # Add test profile tool components
        tool_components = [
            # Компоненты для первого инструмента (1634447.1)
            ProfileToolComponent(tool_id=1, component_type_id=1, variant=1, description="Плита 1 для инструмента 1634447.1", status_id=4),
            ProfileToolComponent(tool_id=1, component_type_id=2, variant=1, description="Плита 2 для инструмента 1634447.1", status_id=4),
            ProfileToolComponent(tool_id=1, component_type_id=5, variant=1, description="Пальцы для инструмента 1634447.1", status_id=3),
            
            # Компоненты для второго инструмента (1540096.0)
            ProfileToolComponent(tool_id=2, component_type_id=1, variant=1, description="Плита 1 для инструмента 1540096.0", status_id=2),
            ProfileToolComponent(tool_id=2, component_type_id=3, variant=2, description="Плита 3 вариант 2 для инструмента 1540096.0", status_id=1),
        ]
        for component in tool_components:
            db.add(component)
        
        # Add test product components
        product_components = [
            ProductComponent(product_id=1, component_name="Основная часть", description="Основная часть фланца", quantity=1),
            ProductComponent(product_id=1, component_name="Ответная часть", description="Ответная часть фланца", quantity=1),
        ]
        for comp in product_components:
            db.add(comp)
        
        db.commit()
        
        # Add test tasks
        tasks = [
            Task(
                profile_tool_id=1,  # Ссылка на инструмент профиля 1634447.1
                department_id=1,
                deadline_on=date(2025, 1, 25),
                position=1,
                status_id=2
            ),
            Task(
                profile_tool_id=2,  # Ссылка на инструмент профиля 1540096.0
                department_id=1,
                deadline_on=date(2025, 1, 30),
                position=2,
                status_id=2
            ),
            Task(
                product_id=1,  # Ссылка на изделие "Фланец"
                department_id=1,
                deadline_on=date(2025, 2, 5),
                position=3,
                status_id=1
            )
        ]
        for task in tasks:
            db.add(task)
        
        db.commit()
        
        # Add test task components
        task_components = [
            # Компоненты для первой задачи (инструмент профиля 1634447.1) - ссылки на компоненты инструмента
            TaskComponent(task_id=1, profile_tool_component_id=1, description="Плита 1 для профиля 1634447.1"),  # Плита 1, вариант 1
            TaskComponent(task_id=1, profile_tool_component_id=2, description="Плита 2 для профиля 1634447.1"),  # Плита 2, вариант 1
            TaskComponent(task_id=1, profile_tool_component_id=3, description="Пальцы для профиля 1634447.1"),   # Пальцы, вариант 1
            
            # Компоненты для второй задачи (инструмент профиля 1540096.0) - ссылка на компонент инструмента
            TaskComponent(task_id=2, profile_tool_component_id=4, description="Плита 1 для профиля 1540096.0"),  # Плита 1, вариант 1
            TaskComponent(task_id=2, profile_tool_component_id=5, description="Плита 3 для профиля 1540096.0"),  # Плита 3, вариант 2
            
            # Компоненты для третьей задачи (изделие "Фланец") - ссылки на компоненты изделия
            TaskComponent(task_id=3, product_component_id=1, description="Основная часть фланца"),
            TaskComponent(task_id=3, product_component_id=2, description="Ответная часть фланца"),
        ]
        for tc in task_components:
            db.add(tc)
        
        db.commit()
        print("Database initialized with test data")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
