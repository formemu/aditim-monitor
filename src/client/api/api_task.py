"""API для работы с задачами"""
from .api_client import ApiClient

class ApiTask(ApiClient):
    """API для задач"""
    def get_task(self):
        """Получение всех задач"""
        return self._request("GET", "api/task")
    
    def get_queue(self):
        """Получить текущую очередь (в статусе 'в работе', с position)"""
        return self._request("GET", "api/task/queue")
    
    def get_task_component(self, task_id):
        """Получение компонентов задач"""
        endpoint = f"api/task/{task_id}/task_component"
        return self._request("GET", endpoint)

    def create_task(self, task_data):
        """Создание новой задачи"""
        return self._request("POST", "api/task", json=task_data)
    
    def create_task_component(self, task_id, component_data):
        """Создание компонента задачи"""
        return self._request("POST", f"api/task/{task_id}/component", json=component_data)

    def create_task_component_stage(self, task_component_id, stage_data):
        """Создание этапа компонента задачи"""
        return self._request("POST", f"api/task/component/{task_component_id}/stage", json=stage_data)

    def reorder_task_queue(self, task_ids: list):
        """Отправить новый порядок очереди"""
        return self._request("POST", "api/task/queue/reorder", json={"task_ids": task_ids})

    def update_task_status(self, task_id, status_id, date):
        """Обновление статуса задачи"""
        return self._request("PATCH", f"api/task/{task_id}/status", json={"status_id": status_id, "completed": date})

    def update_task_location(self, task_id, location_id):
        """Обновление местоположения задачи"""
        return self._request("PATCH", f"api/task/{task_id}/location", json={"location_id": location_id})

    def delete_task(self, task_id):
        """Удаление задачи"""
        return self._request("DELETE", f"api/task/{task_id}")



