"""
API routes for directories
"""

from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.directories import DirDepartament, DirQueueStatus, DirComponent
from ..schemas.directories import DepartamentResponse, StatusResponse, ComponentResponse

router = APIRouter(prefix="/api/directories", tags=["directories"], redirect_slashes=False)


@router.get("/departments", response_model=List[DepartamentResponse])
def get_departments(db: Session = Depends(get_db)):
    """Get all departments"""
    return db.query(DirDepartament).all()


@router.get("/statuses", response_model=List[StatusResponse])
def get_statuses(db: Session = Depends(get_db)):
    """Get all queue statuses"""
    return db.query(DirQueueStatus).all()


@router.get("/components", response_model=List[ComponentResponse])
def get_components(db: Session = Depends(get_db)):
    """Get all components"""
    return db.query(DirComponent).all()
