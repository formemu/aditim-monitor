# src/server/events.py
import asyncio
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections[:]:
            try:
                await connection.send_json(message)
            except RuntimeError:
                self.disconnect(connection)


manager = ConnectionManager()


# === ГЛОБАЛЬНАЯ ССЫЛКА НА ЦИКЛ ===
_loop = None

def get_event_loop():
    """Получает или создаёт event loop для фоновых задач"""
    global _loop
    if _loop is None or _loop.is_closed():
        try:
            _loop = asyncio.get_running_loop()
        except RuntimeError:
            # Если нет running loop — создаём новый (например, в отдельном потоке)
            _loop = asyncio.new_event_loop()
            asyncio.set_event_loop(_loop)
    return _loop


def notify_clients(group: str, key: str, action: str = "updated"):
    """
    Отправить уведомление всем клиентам.
    Работает из синхронного контекста (роутеры).
    """
    message = {
        "event": "data_updated",
        "group": group,
        "key": key,
        "action": action,
        "timestamp": __import__('datetime').datetime.utcnow().isoformat() + 'Z'
    }

    loop = get_event_loop()
    if loop.is_running():
        # Если цикл уже работает — отправляем через threadsafe
        asyncio.run_coroutine_threadsafe(manager.broadcast(message), loop)
    else:
        # Для тестов или standalone-вызовов
        loop.run_until_complete(manager.broadcast(message))