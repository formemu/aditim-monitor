"""
ADITIM Monitor Server - FastAPI application for task management
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import engine, Base
from .api.task import router as tasks_router
from .api.directory import router as directories_router
from .api.product import router as products_router
from .api.profile import router as profiles_router
from .api.profile_tool import router as profile_tools_router

# Import models to register them with SQLAlchemy
from .models.directory import DirDepartment, DirTaskStatus, DirToolDimension, DirComponentType, DirComponentStatus
from .models.product import Product, ProductComponent
from .models.profile import Profile
from .models.profile_tool import ProfileTool, ProfileToolComponent
from .models.task import Task, TaskComponent

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="ADITIM Monitor API",
    description="Task management system for metalworking workshop",
    version="1.0.0",
    redirect_slashes=False
)

# CORS настройки
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(tasks_router)
app.include_router(directories_router)
app.include_router(products_router)
app.include_router(profiles_router)
app.include_router(profile_tools_router)


@app.get("/")
def root():
    """Root endpoint"""
    return {"message": "ADITIM Monitor API is running"}


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "ADITIM Monitor API"}
