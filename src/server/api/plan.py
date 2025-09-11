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
from ..schemas.plan import SchemaPlanTaskComponentStageResponse

router = APIRouter(prefix="/api", tags=["plan"])


# =============================================================================
# GET /plan_task_component_stage - Получить все записи плана стадий компонентов задач
# =============================================================================
@router.get("/plan_task_component_stage", response_model=List[SchemaPlanTaskComponentStageResponse])
def get_plan(
    db: Session = Depends(get_db)
):
    """
    Получает все записи из плана стадий обработки компонентов.
    Включает связанные сущности:
    - component_type (тип компонента)
    - task_component_stage (стадия задачи)

    Используется eager loading (joinedload), чтобы избежать N+1 проблем.
    """
    try:
        # Загружаем основные данные + связи сразу (без lazy loading)
        query = db.query(ModelPlanTaskComponentStage).options(
            joinedload(ModelPlanTaskComponentStage.component_type),
            joinedload(ModelPlanTaskComponentStage.task_component_stage)
        )
        plans = query.all()

        if not plans:
            # Можно вернуть пустой список — это нормально
            return []

        return plans

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