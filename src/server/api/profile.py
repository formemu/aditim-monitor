"""API routes for profile"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.profile import ModelProfile
from ..schemas.profile import SchemaProfileCreate, SchemaProfileUpdate, SchemaProfileResponse
from ..events import notify_clients

router = APIRouter(prefix="/api", tags=["profile"])

# =============================================================================
# ROUTER.GET
# =============================================================================
@router.get("/profile", response_model=List[SchemaProfileResponse])
def get_profile(db: Session = Depends(get_db)):
    return db.query(ModelProfile).all()

# =============================================================================
# ROUTER.POST
# =============================================================================
@router.post("/profile", response_model=SchemaProfileResponse)
def create_profile(profile: SchemaProfileCreate, db: Session = Depends(get_db)):
    profile_data = profile.model_dump()
    if profile_data["sketch"]:
        sketch_str = profile_data["sketch"]
        if isinstance(sketch_str, str) and "," in sketch_str:
            # Убираем data:image/png;base64,
            sketch_str = sketch_str.split(",", 1)[1]
        profile_data["sketch"] = sketch_str  # ← строка

    db_profile = ModelProfile(**profile_data)
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    notify_clients("table", "profile", "created")

    return db_profile

# =============================================================================
# ROUTER.PUT
# =============================================================================
@router.put("/profile/{profile_id}", response_model=SchemaProfileResponse)
def update_profile(profile_id: int, profile: SchemaProfileUpdate, db: Session = Depends(get_db)):
    """Обновить профиль"""
    db_profile = db.query(ModelProfile).filter(ModelProfile.id == profile_id).first()
    if not db_profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    profile_data = profile.model_dump(exclude_unset=True)  # только переданные поля

    # Обработка sketch — сохраняем как Base64 строку
    if "sketch" in profile_data:
        sketch_str = profile_data["sketch"]
        if sketch_str is None:
            db_profile.sketch = None
        else:
            if isinstance(sketch_str, str):
                # Убираем data URL, если есть
                if "," in sketch_str:
                    sketch_str = sketch_str.split(",", 1)[1]
                db_profile.sketch = sketch_str  # ← сохраняем как строку!
            else:
                raise HTTPException(status_code=400, detail="Sketch must be a string")
    # Если sketch не передан — не трогаем

    # Обновляем остальные поля
    for field, value in profile_data.items():
        if field != "sketch":  # sketch уже обработан
            setattr(db_profile, field, value)

    db.commit()
    db.refresh(db_profile)
    notify_clients("table", "profile", "updated")
    return db_profile

# =============================================================================
# ROUTER.DELETE
# =============================================================================
@router.delete("/profile/{profile_id}", response_model=dict)
def delete_profile(profile_id: int, db: Session = Depends(get_db)):
    db_profile = db.query(ModelProfile).filter(ModelProfile.id == profile_id).first()
    if not db_profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    db.delete(db_profile)
    db.commit()
    notify_clients("table", "profile", "deleted")
    notify_clients("table", "profile_tool", "deleted")
    notify_clients("table", "profile_tool_component", "deleted")
    notify_clients("table", "task", "deleted")
    notify_clients("table", "task_component", "deleted")
    notify_clients("table", "queue", "deleted")
    
    return {"detail": "Профиль и все связанные данные удалены"}