"""
API routes for directories
"""

from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.directories import DirDepartment, DirTaskStatus
from ..models.profile_tools import ComponentType, ToolDimension, ComponentStatus
from ..schemas.directories import DepartmentResponse, TaskStatusResponse, ComponentResponse

router = APIRouter(prefix="/api/directories", tags=["directories"], redirect_slashes=False)


@router.get("/departments", response_model=List[DepartmentResponse])
def get_departments(db: Session = Depends(get_db)):
    """Get all departments"""
    return db.query(DirDepartment).all()


@router.get("/task-statuses", response_model=List[TaskStatusResponse])
def get_task_statuses(db: Session = Depends(get_db)):
    """Get all task statuses"""
    return db.query(DirTaskStatus).all()


@router.get("/component-types")
def get_component_types(db: Session = Depends(get_db)):
    """Get all component types from dir_component_types"""
    component_types = db.query(ComponentType).all()
    return [
        {
            "id": ct.id,
            "name": ct.name,
            "description": ct.description or ""
        }
        for ct in component_types
    ]


@router.get("/tool-dimensions")
def get_tool_dimensions(db: Session = Depends(get_db)):
    """Get all tool dimensions from dir_tool_dimensions"""
    dimensions = db.query(ToolDimension).all()
    return [
        {
            "id": dim.id,
            "dimension": dim.dimension,
            "description": dim.description or ""
        }
        for dim in dimensions
    ]


@router.get("/component-statuses")
def get_component_statuses(db: Session = Depends(get_db)):
    """Get all component statuses from dir_component_statuses"""
    statuses = db.query(ComponentStatus).all()
    return [
        {
            "id": status.id,
            "name": status.name,
            "description": status.description or ""
        }
        for status in statuses
    ]
