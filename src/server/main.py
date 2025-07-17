"""
ADITIM Monitor Server - FastAPI application for task management
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import engine, Base
from .api.tasks import router as tasks_router
from .api.directories import router as directories_router
from .api.products import router as products_router

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="ADITIM Monitor API",
    description="Task management system for metalworking workshop",
    version="1.0.0"
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


@app.get("/")
def root():
    """Root endpoint"""
    return {"message": "ADITIM Monitor API is running"}


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "ADITIM Monitor API"}
