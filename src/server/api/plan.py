"""
API роутеры для планов
"""
import traceback
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError

from ..database import get_db
from ..models.plan import ModelPlanTaskComponentStage
from ..schemas.plan import (SchemaPlanTaskComponentStageResponse, 
                            SchemaPlanTaskComponentStageCreate,
                            SchemaPlanTaskComponentStageUpdate)
from ..events import notify_clients

router = APIRouter(prefix="/api", tags=["plan"])


# =============================================================================
# GET /plan_task_component_stage - Получить все записи плана стадий компонентов задач
# =============================================================================
@router.get("/plan_task_component_stage", response_model=List[SchemaPlanTaskComponentStageResponse])
def get_plan(
    db: Session = Depends(get_db)
):
    """ Получает все записи из плана стадий обработки компонентов. """
    try:
        # Загружаем основные данные + связи сразу (без lazy loading)
        query = db.query(ModelPlanTaskComponentStage).all()



        return query

    except SQLAlchemyError as e:
        # Логируем ошибку базы данных
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при обращении к базе данных."
        )

    except Exception as e:
        # Логируем любую другую ошибку
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера."
        )


# =============================================================================
# CRUD для плана стадий (plan_task_component_stage)
# =============================================================================
@router.post("/plan_task_component_stage", response_model=SchemaPlanTaskComponentStageResponse)
def create_plan_task_component_stage(
    plan_stage: SchemaPlanTaskComponentStageCreate,
    db: Session = Depends(get_db)
):
    """Создание нового плана стадии"""
    db_plan_stage = ModelPlanTaskComponentStage(**plan_stage.model_dump())
    db.add(db_plan_stage)
    db.commit()
    db.refresh(db_plan_stage)
    
    # Отправляем сигнал об изменении данных
    notify_clients("plan", "task_component_stage",  "create")

    return db_plan_stage


@router.put("/plan_task_component_stage/{plan_stage_id}", response_model=SchemaPlanTaskComponentStageResponse)
def update_plan_task_component_stage(
    plan_stage_id: int,
    plan_stage: SchemaPlanTaskComponentStageUpdate,
    db: Session = Depends(get_db)
):
    """Обновление плана стадии"""
    db_plan_stage = db.query(ModelPlanTaskComponentStage).filter(
        ModelPlanTaskComponentStage.id == plan_stage_id
    ).first()
    
    if not db_plan_stage:
        raise HTTPException(status_code=404, detail="План стадии не найден")
    
    # Обновляем только переданные поля
    update_data = plan_stage.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_plan_stage, key, value)
    
    db.commit()
    db.refresh(db_plan_stage)
    
    # Отправляем сигнал об изменении данных
    notify_clients("plan", "plan_task_component_stage",  "update")
    
    return db_plan_stage


@router.delete("/plan_task_component_stage/{plan_stage_id}")
def delete_plan_task_component_stage(
    plan_stage_id: int,
    db: Session = Depends(get_db)
):
    """Удаление плана стадии"""
    db_plan_stage = db.query(ModelPlanTaskComponentStage).filter(
        ModelPlanTaskComponentStage.id == plan_stage_id
    ).first()
    
    if not db_plan_stage:
        raise HTTPException(status_code=404, detail="План стадии не найден")
    
    db.delete(db_plan_stage)
    db.commit()
    
    # Отправляем сигнал об изменении данных
    notify_clients("plan", "plan_task_component_stage",  "delete")

    return {"status": "success", "message": "План стадии удален"}
