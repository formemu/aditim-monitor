"""
API routes for profiles
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import base64

from ..database import get_db
from ..models.profile import Profile
from ..schemas.product import ProfileCreate, ProfileResponse

router = APIRouter(prefix="/api", tags=["profiles"])


@router.get("/profile", response_model=List[ProfileResponse])
def get_profile(db: Session = Depends(get_db)):
    """Get all profile (единственное число)"""
    return db.query(Profile).all()


@router.post("/profile", response_model=ProfileResponse)
def create_profile(profile: ProfileCreate, db: Session = Depends(get_db)):
    """Create a new profile (единственное число)"""
    profile_data = profile.dict()
    
    # Convert base64 image to binary if provided
    if profile_data.get("sketch"):
        try:
            # Remove data URI prefix if present (data:image/png;base64,...)
            sketch_data = profile_data["sketch"]
            if sketch_data.startswith("data:"):
                sketch_data = sketch_data.split(",", 1)[1]
            
            # Decode base64 to binary
            profile_data["sketch"] = base64.b64decode(sketch_data)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid image data: {e}")
    
    db_profile = Profile(**profile_data)
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    return db_profile


# @router.get("/profile/{profile_id}", response_model=ProfileResponse) # НЕ ИСПОЛЬЗУЕТСЯ
# def get_profile_by_id(profile_id: int, db: Session = Depends(get_db)):
#     """Get profile by ID (единственное число)"""
#     profile = db.query(Profile).filter(Profile.id == profile_id).first()
#     if not profile:
#         raise HTTPException(status_code=404, detail="Profile not found")
#     return profile


@router.delete("/profile/{profile_id}", response_model=dict)
def delete_profile(profile_id: int, db: Session = Depends(get_db)):
    """Удалить профиль по profile_id (единственное число)"""
    profile = db.query(Profile).filter(Profile.id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    db.delete(profile)
    db.commit()
    return {"success": True, "deleted": 1}
