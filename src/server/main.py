"""
ADITIM Monitor Server - FastAPI application for task management
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import engine, Base
from .api.task import router as tasks_router
from .api.directory import router as directory_router
from .api.product import router as product_router
from .api.profile import router as profile_router
from .api.profile_tool import router as profile_tool_router

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="ADITIM Monitor API",
    description="Task management system for metalworking workshop",
    version="1.0.0",
    redirect_slashes=False,
    debug=True
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
app.include_router(directory_router)
app.include_router(product_router)
app.include_router(profile_router)
app.include_router(profile_tool_router)


@app.get("/")
def root():
    """Root endpoint"""
    return {"message": "ADITIM Monitor API is running"}


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "ADITIM Monitor API"}
