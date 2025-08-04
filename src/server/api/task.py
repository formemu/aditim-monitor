"""
API роутеры для задач
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.task import Task, TaskComponent
from ..models.product import Product
from ..models.profile_tool import ProfileTool
from ..models.directory import DirTaskStatus
from ..schemas.task import TaskCreate, TaskUpdate, TaskResponse, TaskStatusUpdateRequest

router = APIRouter(prefix="/api/task", tags=["task"])

# ----------------------------------------------------------------------
# Получение списка задач
# ----------------------------------------------------------------------
@router.get("/", response_model=List[TaskResponse])
def get_task_list(
    status: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Получить список задач с необязательным фильтром по статусу"""
    query = db.query(Task)
    if status:
        query = query.join(DirTaskStatus).filter(DirTaskStatus.name == status)
    tasks = query.order_by(Task.position).limit(limit).all()
    return tasks

# ----------------------------------------------------------------------
# Получение задачи по ID
# ----------------------------------------------------------------------
@router.get("/{task_id}", response_model=TaskResponse)
def get_task_by_id(
    task_id: int = Path(..., description="ID задачи", ge=1),
    db: Session = Depends(get_db)
):
    """Получить задачу по ID"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    return task

# ----------------------------------------------------------------------
# Создание новой задачи
# ----------------------------------------------------------------------
@router.post("/", response_model=TaskResponse)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    """Создать новую задачу с корректной позицией для статуса 'в работе'"""
    task_data = task.dict()

    # Обработка продукта
    if task.product_id and isinstance(task.product_id, str):
        product_name = task.product_id
        product = db.query(Product).filter(Product.name == product_name).first()
        if not product:
            product = Product(name=product_name, department_id=task.department_id)
            db.add(product)
            db.commit()
            db.refresh(product)
        task_data["product_id"] = product.id
    elif task.product_id:
        product = db.query(Product).filter(Product.id == task.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Продукт не найден")

    # Проверка инструмента профиля
    if task_data.get("profile_tool_id"):
        profile_tool = db.query(ProfileTool).filter(ProfileTool.id == task_data["profile_tool_id"]).first()
        if not profile_tool:
            raise HTTPException(status_code=404, detail="Инструмент профиля не найден")

    # Получаем id статуса "в работе"
    dir_task_status = db.query(DirTaskStatus).filter(DirTaskStatus.name == "в работе").first()
    in_work_status_id = dir_task_status.id if dir_task_status else None

    # Назначаем позицию только если статус "в работе"
    position = None
    if task_data.get("status_id") == in_work_status_id:
        max_position = db.query(Task).filter(Task.status_id == in_work_status_id).count()
        position = max_position + 1
    task_data["position"] = position

    db_task = Task(**task_data)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

# ----------------------------------------------------------------------
# Обновление задачи
# ----------------------------------------------------------------------
@router.put("/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, task_update: TaskUpdate, db: Session = Depends(get_db)):
    """Обновить задачу"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    for field, value in task_update.dict(exclude_unset=True).items():
        setattr(task, field, value)
    db.commit()
    db.refresh(task)
    return task

# ----------------------------------------------------------------------
# Обновление статуса задачи
# ----------------------------------------------------------------------
@router.patch("/{task_id}/status")
def update_task_status(
    task_id: int,
    request: TaskStatusUpdateRequest,
    db: Session = Depends(get_db)
):
    """Обновить статус задачи"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    task.status_id = request.status_id
    db.commit()
    db.refresh(task)
    return {"message": "Статус задачи обновлен", "task_id": task_id, "status_id": request.status_id}

# ----------------------------------------------------------------------
# Обновление позиции задачи
# ----------------------------------------------------------------------
@router.put("/{task_id}/position")
def update_task_position(task_id: int, position: int, db: Session = Depends(get_db)):
    """Обновить позицию задачи в очереди"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    task.position = position
    db.commit()
    return {"message": "Позиция задачи обновлена"}

# ----------------------------------------------------------------------
# Удаление задачи
# ----------------------------------------------------------------------
@router.delete("/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    """Удалить задачу"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    db.delete(task)
    db.commit()
    return {"message": "Задача удалена"}


# ----------------------------------------------------------------------
# Получение компонентов задачи
# ----------------------------------------------------------------------
@router.get("/{task_id}/task_component")
def get_task_component_list(
    task_id: int = Path(..., description="ID задачи", ge=1),
    db: Session = Depends(get_db)
):
    """Получить компоненты задачи по ID задачи"""
    try:
        query = db.query(TaskComponent).filter(TaskComponent.task_id == task_id)
        component = query.all()
        result = []
        for comp in component:
            comp_dict = {
                "id": comp.id,
                "task_id": comp.task_id,
                "profile_tool_component_id": comp.profile_tool_component_id,
                "product_component_id": comp.product_component_id,
                "quantity": comp.quantity
            }
            # Определяем тип компонента и получаем данные
            if comp.profile_tool_component_id and comp.profile_tool_component:
                name = (
                    comp.profile_tool_component.component_type.name
                    if comp.profile_tool_component.component_type
                    else "Неизвестный компонент"
                )
                variant = comp.profile_tool_component.variant
                if variant:
                    name = f"{name} (вариант {variant})"
                comp_dict["name"] = name
                comp_dict["quantity"] = 1
            elif comp.product_component_id and comp.product_component:
                comp_dict["name"] = comp.product_component.component_name
                comp_dict["quantity"] = comp.quantity or 1
            else:
                comp_dict["name"] = "Неизвестный компонент"
                comp_dict["quantity"] = 1
            result.append(comp_dict)
        return result
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal server error")
# ----------------------------------------------------------------------
# Создание компонента задачи
# ----------------------------------------------------------------------
@router.post("/task_component")
def create_task_component(component_data: dict, db: Session = Depends(get_db)):
    """Создать компонент задачи"""
    try:
        if "task_id" not in component_data:
            raise HTTPException(status_code=400, detail="Поле task_id обязательно")

        component = TaskComponent(task_id=component_data["task_id"])

        pt_comp_id = component_data.get("profile_tool_component_id")
        prod_comp_id = component_data.get("product_component_id")

        if pt_comp_id:
            component.profile_tool_component_id = pt_comp_id
            component.quantity = component_data.get("quantity", 1)
        elif prod_comp_id:
            component.product_component_id = prod_comp_id
            component.quantity = component_data.get("quantity", 1)
        else:
            raise HTTPException(
                status_code=400,
                detail="Укажите profile_tool_component_id или product_component_id"
            )

        db.add(component)
        db.commit()
        db.refresh(component)

        result = {
            "id": component.id,
            "task_id": component.task_id,
            "profile_tool_component_id": component.profile_tool_component_id,
            "product_component_id": component.product_component_id,
            "quantity": component.quantity
        }
        # Добавим name для согласованности
        if component.profile_tool_component_id and component.profile_tool_component:
            name = (
                component.profile_tool_component.component_type.name
                if component.profile_tool_component.component_type
                else "Неизвестный компонент"
            )
            variant = component.profile_tool_component.variant
            if variant:
                name = f"{name} (вариант {variant})"
            result["name"] = name
        elif component.product_component_id and component.product_component:
            result["name"] = component.product_component.component_name
        else:
            result["name"] = "Неизвестный компонент"
        return result

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=f"Ошибка создания: {str(e)}")