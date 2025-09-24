# src/server/api/task_component_stage.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.task import ModelTaskComponentStage
from pydantic import BaseModel
from datetime import date

router = APIRouter(prefix="/api/task/component/stage", tags=["task-component-stage"])

# === Pydantic Schemas ===
class SchemaTaskComponentStageUpdate(BaseModel):
    start: date | None = None
    finish: date | None = None

    class Config:
        from_attributes = True


# === ROUTES ===
@router.patch("/{stage_id}")
def update_stage(
    stage_id: int,
    data: SchemaTaskComponentStageUpdate,
    db: Session = Depends(get_db)
):
    """Обновление дат начала и окончания этапа"""
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

    db.commit()
    db.refresh(stage)
    return stage