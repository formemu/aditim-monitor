# src/server/api/task_component_stage.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.task import ModelTaskComponentStage
from ..schemas.task import SchemaTaskComponentStageUpdate

from ..events import notify_clients

router = APIRouter(prefix="/api/task/component/stage", tags=["task-component-stage"])




# === ROUTES ===
@router.patch("/{stage_id}")
def update_stage(
    stage_id: int,
    data: SchemaTaskComponentStageUpdate,
    db: Session = Depends(get_db)
):
    """Обновление дат начала и окончания этапа, а также привязка к станку"""
    stage = db.query(ModelTaskComponentStage).filter(
        ModelTaskComponentStage.id == stage_id
    ).first()

    if not stage:
        raise HTTPException(status_code=404, detail="Этап не найден")

    # Обновляем только переданные поля
    if data.start is not None:
        stage.start = data.start
    if data.finish is not None:
        stage.finish = data.finish
    if data.machine_id is not None:
        stage.machine_id = data.machine_id
    
    notify_clients("table", "task", "updated")
    notify_clients("table", "taskdev", "updated")
    db.commit()
    db.refresh(stage)
    return stage