"""
API routes for tasks
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.task import Task
from ..models.product import Product
from ..models.profile_tool import ProfileTool
from ..models.task import TaskComponent
from ..models.directory import DirTaskStatus
from ..models.task import TaskComponent
from ..schemas.task import TaskCreate, TaskUpdate, TaskResponse

router = APIRouter(prefix="/api/task", tags=["task"])


@router.get("/", response_model=List[TaskResponse])
def get_task_list(
    status: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all tasks with optional status filter"""
    query = db.query(Task)
    
    if status:
        query = query.join(DirTaskStatus).filter(DirTaskStatus.name == status)
    
    task = query.order_by(Task.position).limit(limit).all()
    return task

@router.post("/", response_model=TaskResponse)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    """Create a new task"""
    task_data = task.dict()
    
    # Handle product creation/lookup
    if task.product_id and isinstance(task.product_id, str):
        # If product_id is a string, treat it as product name and create/find product
        product_name = task.product_id
        product = db.query(Product).filter(Product.name == product_name).first()
        if not product:
            # Create new product
            product = Product(name=product_name, department_id=task.department_id)
            db.add(product)
            db.commit()
            db.refresh(product)
        task_data["product_id"] = product.id
    elif task.product_id:
        # If it's an integer, validate it exists
        product = db.query(Product).filter(Product.id == task.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
    
    # Handle profile_tool validation
    if task_data.get("profile_tool_id"):
        profile_tool = db.query(ProfileTool).filter(ProfileTool.id == task_data["profile_tool_id"]).first()
        if not profile_tool:
            raise HTTPException(status_code=404, detail="Profile tool not found")
    
    # Create task
    db_task = Task(**task_data)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    
    return db_task

# === Task Component endpoints ===
@router.get("/task-component")
def get_task_component_list(task_id: Optional[int] = None, db: Session = Depends(get_db)):
    """Get all task components, optionally filtered by task_id"""
    try:
        # Получаем все компоненты задач
        query = db.query(TaskComponent)
        
        # Фильтрация по task_id если указан
        if task_id:
            query = query.filter(TaskComponent.task_id == task_id)
        
        components = query.all()
        
        result = []
        for comp in components:
            comp_dict = {
                "id": comp.id,
                "task_id": comp.task_id,
                "profile_tool_component_id": comp.profile_tool_component_id,
                "product_component_id": comp.product_component_id,
                "quantity": comp.quantity
            }
            # Определяем тип компонента и получаем данные
            if comp.profile_tool_component_id and comp.profile_tool_component:
                # Компонент инструмента профиля
                name = comp.profile_tool_component.component_type.name if comp.profile_tool_component.component_type else "Неизвестный компонент"
                variant = comp.profile_tool_component.variant
                if variant:
                    name = f"{name} (вариант {variant})"
                comp_dict["name"] = name
                comp_dict["quantity"] = 1  # По умолчанию для компонентов инструментов
                
            elif comp.product_component_id and comp.product_component:
                # Компонент изделия
                comp_dict["name"] = comp.product_component.component_name
                comp_dict["quantity"] = comp.quantity or 1
                
            else:
                # Компонент без связи
                comp_dict["name"] = "Неизвестный компонент"
                comp_dict["quantity"] = 1
            
            result.append(comp_dict)
        
        return result
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return []

@router.post("/task-component")
def create_task_component(component_data: dict, db: Session = Depends(get_db)):
    """Create new task component"""
    try:
        # Определяем тип компонента и создаем соответствующую запись
        component = TaskComponent(task_id=component_data["task_id"])
        
        # Проверяем какой тип компонента передан
        if "profile_tool_component_id" in component_data and component_data["profile_tool_component_id"]:
            # Компонент инструмента профиля
            component.profile_tool_component_id = component_data["profile_tool_component_id"]
            component.quantity = component_data.get("quantity", 1)
            
        elif "product_component_id" in component_data and component_data["product_component_id"]:
            # Компонент изделия
            component.product_component_id = component_data["product_component_id"]
            component.quantity = component_data.get("quantity", 1)

        else:
            raise HTTPException(
                status_code=400, 
                detail="Необходимо указать profile_tool_component_id или product_component_id"
            )
        
        db.add(component)
        db.commit()
        db.refresh(component)
        
        # Формируем ответ с учетом типа компонента
        result = {
            "id": component.id,
            "task_id": component.task_id,
            "profile_tool_component_id": component.profile_tool_component_id,
            "product_component_id": component.product_component_id,
            "quantity": component.quantity
        }
        return result
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{task_id}", response_model=TaskResponse)
def get_task_by_id(task_id: int, db: Session = Depends(get_db)):
    """Get task by ID"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.put("/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, task_update: TaskUpdate, db: Session = Depends(get_db)):
    """Update task"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Update fields
    for field, value in task_update.dict(exclude_unset=True).items():
        setattr(task, field, value)
    
    db.commit()
    db.refresh(task)
    return task

@router.delete("/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    """Delete task"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db.delete(task)
    db.commit()
    return {"message": "Task deleted successfully"}

@router.put("/{task_id}/position")
def update_task_position(task_id: int, position: int, db: Session = Depends(get_db)):
    """Update task position in queue"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task.position = position
    db.commit()
    return {"message": "Task position updated successfully"}
