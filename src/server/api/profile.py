"""API routes for profile"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import base64

from ..database import get_db
from ..models.profile import Profile
from ..schemas.profile import ProfileCreate, ProfileResponse, ProfileUpdate

router = APIRouter(prefix="/api", tags=["profiles"])


# =============================================================================
# ROUTER.GET
# =============================================================================
@router.get("/profile", response_model=List[ProfileResponse])
def get_profile(db: Session = Depends(get_db)):
    """Получить все профили"""
    return db.query(Profile).all()

# =============================================================================
# ROUTER.POST
# =============================================================================
@router.post("/profile", response_model=ProfileResponse)
def create_profile(profile: ProfileCreate, db: Session = Depends(get_db)):
    """Создать новый профиль"""
    profile_data = profile.model_dump()
    if profile_data.get("sketch"):
            sketch_data = profile_data["sketch"]
            if sketch_data.startswith("data:"):
                sketch_data = sketch_data.split(",", 1)[1]
            profile_data["sketch"] = base64.b64decode(sketch_data)
    db_profile = Profile(**profile_data)
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    return db_profile

# =============================================================================
# ROUTER.PUT
# =============================================================================
@router.put("/profile/{profile_id}")
def update_profile(profile_id: int, profile: ProfileUpdate, db: Session = Depends(get_db)):
    """Обновить профиль"""
    # Найти существующий профиль
    db_profile = db.query(Profile).filter(Profile.id == profile_id).first()
    if db_profile:
        profile_data = profile.model_dump()
        if profile_data.get("sketch"):
            sketch_data = profile_data["sketch"]
            if sketch_data.startswith("data:"):
                sketch_data = sketch_data.split(",", 1)[1]
            profile_data["sketch"] = base64.b64decode(sketch_data)
        for field, value in profile_data.items():
            if value is not None:  # Только обновляем поля, которые не None
                setattr(db_profile, field, value)
    else:
        raise HTTPException(status_code=404, detail="Profile not found")

    db.commit()
    db.refresh(db_profile)

# =============================================================================
# ROUTER.DELETE
# =============================================================================
@router.delete("/profile/{profile_id}")
def delete_profile(profile_id: int, db: Session = Depends(get_db)):
    """Удалить профиль по profile_id"""
    profile = db.query(Profile).filter(Profile.id == profile_id).first()
    if  profile:
        db.delete(profile)
        db.commit()
    else:
        raise HTTPException(status_code=404, detail="Profile not found")

