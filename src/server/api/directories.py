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


@router.get("/department", response_model=List[DepartmentResponse])
def get_department(db: Session = Depends(get_db)):
    """Get all department (единственное число)"""
    return db.query(DirDepartment).all()


@router.get("/task-status", response_model=List[TaskStatusResponse])
def get_task_status(db: Session = Depends(get_db)):
    """Get all task status (единственное число)"""
    return db.query(DirTaskStatus).all()


@router.get("/component-type")
def get_component_type(db: Session = Depends(get_db)):
    """Get all component type from dir_component_type (единственное число)"""
    component_types = db.query(ComponentType).all()
    return [
        {
            "id": ct.id,
            "name": ct.name,
            "description": ct.description or ""
        }
        for ct in component_types
    ]


@router.get("/tool-dimension")
def get_tool_dimension(db: Session = Depends(get_db)):
    """Get all tool dimension from dir_tool_dimension (единственное число)"""
    dimensions = db.query(ToolDimension).all()
    return [
        {
            "id": dim.id,
            "dimension": dim.dimension,
            "description": dim.description or ""
        }
        for dim in dimensions
    ]


@router.get("/component-status")
def get_component_status(db: Session = Depends(get_db)):
    """Get all component status from dir_component_status (единственное число)"""
    statuses = db.query(ComponentStatus).all()
    return [
        {
            "id": status.id,
            "name": status.name,
            "description": status.description or ""
        }
        for status in statuses
    ]
