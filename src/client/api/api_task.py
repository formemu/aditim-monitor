"""API для работы с задачами"""
from .api_client import ApiClient


class ApiTask(ApiClient):
    """API для задач"""

    def get_task(self):
        """Получение всех задач"""
        return self._request("GET", "api/task/")

    def create_task(self, task_data):
        """Создание новой задачи"""
        return self._request("POST", "api/task/", json=task_data)

    def update_task_status(self, task_id, status_id):
        """Обновление статуса задачи"""
        return self._request("PATCH", f"api/task/{task_id}/status", json={"status_id": status_id})

    def update_task_position(self, task_id, position):
        """Обновление позиции задачи"""
        return self._request("PATCH", f"api/task/{task_id}/position", json={"position": position})

    def delete_task(self, task_id):
        """Удаление задачи"""
        return self._request("DELETE", f"api/task/{task_id}")

    def get_task_component(self, task_id):
        """Получение компонентов задач"""
        endpoint = f"api/task/{task_id}/task_component"
        return self._request("GET", endpoint)

    def create_task_component(self, component_data):
        """Создание компонента задачи"""
        return self._request("POST", "api/task/task_component", json=component_data)