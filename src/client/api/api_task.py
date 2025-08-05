"""
API для работы с задачами
"""

from .api_client import ApiClient
from typing import List, Dict, Any


class ApiTask(ApiClient):
    """API для задач"""

    def get_task(self) -> List[Dict[Any, Any]]:
        """Получение всех задач"""
        return self._request("GET", "api/task/")

    def create_task(self, task_data: Dict[str, Any]) -> Dict[Any, Any]:
        """Создание новой задачи"""
        return self._request("POST", "api/task/", json=task_data)

    def update_task(self, task_id: int, task_data: Dict[str, Any]) -> Dict[Any, Any]:
        """Обновление задачи"""
        return self._request("PUT", f"api/task/{task_id}", json=task_data)

    def update_task_status(self, task_id: int, status_id: int) -> Dict[Any, Any]:
        """Обновление статуса задачи"""
        return self._request("PATCH", f"api/task/{task_id}/status", json={"status_id": status_id})

    def update_task_position(self, task_id: int, position: int) -> Dict[Any, Any]:
        """Обновление позиции задачи"""
        return self._request("PATCH", f"api/task/{task_id}/position", json={"position": position})

    def delete_task(self, task_id: int) -> Dict[Any, Any]:
        """Удаление задачи"""
        return self._request("DELETE", f"api/task/{task_id}")

    def get_task_component(self, task_id: int) -> List[Dict[Any, Any]]:
        """Получение компонентов задач"""
        endpoint = f"api/task/{task_id}/task_component"
        return self._request("GET", endpoint)

    def create_task_component(self, component_data: Dict[str, Any]) -> Dict[Any, Any]:
        """Создание компонента задачи"""
        return self._request("POST", "api/task/task_component", json=component_data)