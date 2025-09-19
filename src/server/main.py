"""
ADITIM Monitor Server - FastAPI application for task management
"""

from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# === ВАЖНО: Импортируем manager ДО объявления app ===
from .events import manager

# Подключаем роутеры (все импорты после создания app)
from .api.task import router as tasks_router
from .api.directory import router as directory_router
from .api.product import router as product_router
from .api.profile import router as profile_router
from .api.profile_tool import router as profile_tool_router
from .api.plan import router as plan_router

app = FastAPI(
    title="ADITIM Monitor API",
    description="Task management system for metalworking workshop",
    version="1.0.0",
    redirect_slashes=False,
    debug=True
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Замени на конкретные домены в продакшене
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



app.include_router(tasks_router)
app.include_router(directory_router)
app.include_router(product_router)
app.include_router(profile_router)
app.include_router(profile_tool_router)
app.include_router(plan_router)


# === Вебсокет эндпоинт ===
@app.websocket("/ws/updates")
async def websocket_endpoint(websocket: WebSocket):
    """
    Вебсокет для передачи уведомлений клиентам.
    Клиент может просто подключиться и слушать события.
    """
    await manager.connect(websocket)
    try:
        while True:
            # Можно принимать пинг или команды (не обязательно)
            await websocket.receive_text()
    except Exception as e:
        pass
    finally:
        manager.disconnect(websocket)


# === Корневые эндпоинты ===
@app.get("/")
def root():
    return {"message": "ADITIM Monitor API is running"}


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "ADITIM Monitor API"}