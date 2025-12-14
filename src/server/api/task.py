"""API роутеры для задач"""
import traceback
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body
from sqlalchemy.orm import Session , selectinload
from ..database import get_db
from ..models.task import ModelTask, ModelTaskComponent, ModelTaskComponentStage
from ..models.profiletool import ModelProfileTool, ModelProfileToolComponent
from ..models.blank import ModelBlank
from ..models.directory import ModelDirTaskStatus, ModelDirTaskType
from ..schemas.task import (
    SchemaTaskCreate,
    SchemaTaskUpdate,
    SchemaTaskComponentCreate,
    SchemaTaskResponse,
    SchemaTaskComponentResponse,
    SchemaQueueReorderRequest,
    SchemaTaskComponentStageCreate
)
from ..events import notify_clients

router = APIRouter(prefix="/api", tags=["task"])

# =============================================================================
# ROUTER.GET
# =============================================================================

@router.get("/task", response_model=List[SchemaTaskResponse])
def get_task(db: Session = Depends(get_db)):
    """Получить все задачи с загрузкой связанных данных"""
    return db.query(ModelTask).options(
        selectinload(ModelTask.profiletool).selectinload(ModelProfileTool.profile),
        selectinload(ModelTask.product),
        selectinload(ModelTask.status),
        selectinload(ModelTask.type),
        selectinload(ModelTask.location),
        selectinload(ModelTask.component).selectinload(ModelTaskComponent.stage),
        selectinload(ModelTask.component).selectinload(ModelTaskComponent.profiletool_component).selectinload(ModelProfileToolComponent.blank).selectinload(ModelBlank.material)
    ).order_by(ModelTask.id).all()

@router.get("/taskdev", response_model=List[SchemaTaskResponse])
def get_taskdev(db: Session = Depends(get_db)):
    """Получить задачи в разработке с загрузкой связанных данных"""
    type = db.query(ModelDirTaskType).filter(ModelDirTaskType.name == "Разработка").first()
    status = db.query(ModelDirTaskStatus).filter(ModelDirTaskStatus.name == "В работе").first()
    return db.query(ModelTask).options(
        selectinload(ModelTask.profiletool).selectinload(ModelProfileTool.profile),
        selectinload(ModelTask.product),
        selectinload(ModelTask.status),
        selectinload(ModelTask.type),
        selectinload(ModelTask.location),
        selectinload(ModelTask.component).selectinload(ModelTaskComponent.stage)
    ).filter(ModelTask.type_id == type.id, ModelTask.status_id == status.id).order_by(ModelTask.position).all()

@router.get("/task/queue", response_model=List[SchemaTaskResponse])
def get_queue(db: Session = Depends(get_db)):
    """Получить очередь задач с загрузкой связанных данных"""
    status_in_progress = db.query(ModelDirTaskStatus).filter(ModelDirTaskStatus.name == "В работе").first()
    return db.query(ModelTask).options(
        selectinload(ModelTask.profiletool).selectinload(ModelProfileTool.profile),
        selectinload(ModelTask.product),
        selectinload(ModelTask.status),
        selectinload(ModelTask.type),
        selectinload(ModelTask.location),
        selectinload(ModelTask.component).selectinload(ModelTaskComponent.stage)
    ).filter(ModelTask.status_id == status_in_progress.id, ModelTask.position.isnot(None)).order_by(ModelTask.position).all()



# @router.get("/task/{task_id}/component", response_model=List[SchemaTaskComponentResponse])
# def get_task_component_list(task_id: int, db: Session = Depends(get_db)):
#     """Получить компоненты задачи по ID задачи"""``
#     return db.query(ModelTaskComponent).filter(ModelTaskComponent.task_id == task_id).all()

# =============================================================================
# ROUTER.POST
# =============================================================================
@router.post("/task", response_model=SchemaTaskResponse)
def create_task(task: SchemaTaskCreate, db: Session = Depends(get_db)):
    """Создать новую задачу"""
    try:
        task = ModelTask(
            product_id=task.product_id,
            profiletool_id=task.profiletool_id,
            deadline=task.deadline,
            position=task.position,
            status_id=task.status_id,
            type_id=task.type_id,
            description=task.description,
            created=task.created
        )
        
        db.add(task)
        db.commit()
        db.refresh(task)
        notify_clients("table", "task", "created")
        return task
    except Exception as e:
        db.rollback()
        # print("❌ ОШИБКА ПРИ СОЗДАНИИ ЗАДАЧИ")
        # print(f"Тип ошибки: {type(e).__name__}")
        # print(f"Сообщение: {str(e)}")
        # print("----- TRACEBACK -----")
        # traceback.print_exc()  # ← Это покажет, где именно ошибка
        raise HTTPException(status_code=500, detail=f"Не удалось создать задачу: {type(e).__name__}: {str(e)}")

@router.post("/task/{task_id}/component", response_model=SchemaTaskComponentResponse)
def create_task_component(
    task_id: int = Path(..., description="ID задачи"),
    component: SchemaTaskComponentCreate = Body(...),
    db: Session = Depends(get_db)
):
    """Создать новый компонент задачи"""

    # Создаём компонент
    if component.profiletool_component_id:
        db_component = ModelTaskComponent(
            task_id=task_id,
            profiletool_component_id=component.profiletool_component_id,
            description=component.description
        )
    elif component.product_component_id:
        db_component = ModelTaskComponent(
            task_id=task_id,
            product_component_id=component.product_component_id,
            description=component.description
        )
    else:
        raise HTTPException(
            status_code=422,
            detail="Требуется profiletool_component_id или product_component_id"
        )

    db.add(db_component)
    db.commit()
    db.refresh(db_component)
    notify_clients("table", "task", "updated")
    return db_component

@router.post("/task/component/{component_id}/stage", response_model=dict)
def create_task_component_stage(component_id: int, stage_data: SchemaTaskComponentStageCreate, db: Session = Depends(get_db)):
    """    Добавить этап к компоненту задачи  """
    # Создаём запись
    stage = ModelTaskComponentStage(
        task_component_id=component_id,
        work_subtype_id=stage_data.work_subtype_id,
        machine_id=stage_data.machine_id,
        stage_num=stage_data.stage_num,
        description=stage_data.description or ""
    )

    db.add(stage)
    db.commit()
    db.refresh(stage)
    notify_clients("table", "task_component_stage", "created")
    return {"id": stage.id}

@router.post("/task/queue/reorder", status_code=204)
def reorder_queue(request: SchemaQueueReorderRequest, db: Session = Depends(get_db)):
    """Изменение порядка задач в очереди"""
    # 1. Сбросить позиции у задач у всех
    db.query(ModelTask).update({ModelTask.position: None}, synchronize_session='fetch')
    # 2. Установить новые позиции для переданных задач
    for position, task_id in enumerate(request.task_ids, start=1):
        db.query(ModelTask).filter(ModelTask.id == task_id).update({ModelTask.position: position}, synchronize_session='fetch')
    notify_clients("table", "task", "updated")
    notify_clients("table", "queue", "updated")   
    db.commit()

# =============================================================================
# ROUTER.PATCH
# ===========================================================================
@router.patch("/task/{task_id}/status", response_model=SchemaTaskResponse)
def update_task_status( task_id: int, task: SchemaTaskUpdate, db: Session = Depends(get_db)):
    """Обновить статус задачи"""
    status_completed = db.query(ModelDirTaskStatus).filter(ModelDirTaskStatus.name == "Выполнена").first()
    print(status_completed)
    db_task = db.get(ModelTask, task_id)
    db_task.status_id = task.status_id
    if task.status_id == status_completed.id:
        db_task.completed = task.completed
    else:
        db_task.completed = None
    db.commit()
    db.refresh(db_task)
    notify_clients("table", "task", "updated")
    notify_clients("table", "taskdev", "updated")
    notify_clients("table", "queue", "updated")
    return db_task

# Обновление местоположения задачи
@router.patch("/task/{task_id}/location", response_model=SchemaTaskResponse)
def update_task_location(task_id: int, task: SchemaTaskUpdate, db: Session = Depends(get_db)):
    """Обновить местоположение задачи"""
    db_task = db.get(ModelTask, task_id)
    db_task.location_id = task.location_id
    db.commit()
    db.refresh(db_task)
    notify_clients("table", "task", "updated")
    return db_task


# =============================================================================
# ROUTER.DELETE
# =============================================================================
@router.delete("/task/{task_id}", response_model=dict)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    """Удалить задачу по ID с каскадным удалением компонентов"""
    # Используем query с явной загрузкой связей для корректного каскадного удаления
    db_task = db.query(ModelTask).options(
        selectinload(ModelTask.component).selectinload(ModelTaskComponent.stage)
    ).filter(ModelTask.id == task_id).first()
    
    if not db_task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    
    db.delete(db_task)
    db.commit()
    notify_clients("table", "task", "deleted")
    return {"detail": "Задача удалена успешно"}