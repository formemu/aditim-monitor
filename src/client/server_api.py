import httpx
from typing import Any, Dict, List
from constants import API_URL

class ServerAPI:

    """
    Класс для работы с сервером FastAPI.
    Предоставляет статические методы для получения и обновления данных задач.
    """
    
    @staticmethod
    def check_profile_article(article: str) -> dict:
        """
        Проверка существования профиля по артикулу.
        """
        with httpx.Client() as client:
            resp = client.get(f"http://localhost:8000/profile_types/check_article/{article}")
            resp.raise_for_status()
            return resp.json()

    @staticmethod
    def create_profile_type(article: str, name: str) -> dict:
        """
        Создание нового профиля по артикулу и имени.
        """
        with httpx.Client() as client:
            resp = client.post("http://localhost:8000/profile_types", json={"article": article, "name": name})
            resp.raise_for_status()
            return resp.json()


    @staticmethod
    def get_tasks(active_only: bool) -> List[Dict[str, Any]]:
        with httpx.Client() as client:
            resp = client.get(API_URL, params={"active_only": 0 if active_only else 1})
            resp.raise_for_status()
            return resp.json()
        
    @staticmethod    
    def get_departaments() -> List[Dict[str, Any]]:
        with httpx.Client() as client:
            resp = client.get("http://localhost:8000/departaments")
            resp.raise_for_status()
            return resp.json()

    @staticmethod
    def get_statuses() -> List[Dict[str, Any]]:
        with httpx.Client() as client:
            resp = client.get("http://localhost:8000/dir_queue_status")
            resp.raise_for_status()
            return resp.json()

    @staticmethod
    def patch_status(task_id: int, status_id: int) -> httpx.Response:
        with httpx.Client() as client:
            resp = client.patch(f"{API_URL}/{task_id}/status", json={"id_status": status_id})
            return resp

    @staticmethod
    def add_task(payload: Dict[str, Any]) -> httpx.Response:
        with httpx.Client() as client:
            resp = client.post(API_URL, json=payload)
            return resp

    @staticmethod
    def update_positions(positions: List[Dict[str, Any]]) -> httpx.Response:
        """
        Массовое обновление позиций задач на сервере.
        """
        with httpx.Client() as client:
            resp = client.patch(f"{API_URL}/positions", json=positions)
            return resp
