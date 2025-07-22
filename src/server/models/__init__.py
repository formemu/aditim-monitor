"""
Models package for ADITIM Monitor
"""

# Import all models to ensure they are registered with SQLAlchemy
from .directories import DirDepartment, DirTaskStatus
from .products import Product, Profile, ProductComponent
from .profile_tools import ToolDimension, ComponentType, ComponentStatus, ProfileTool, ProfileToolComponent
from .tasks import Task, TaskComponent

__all__ = [
    'DirDepartment', 'DirTaskStatus',
    'Product', 'Profile', 'ProductComponent',
    'ToolDimension', 'ComponentType', 'ComponentStatus', 'ProfileTool', 'ProfileToolComponent',
    'Task', 'TaskComponent'
]
