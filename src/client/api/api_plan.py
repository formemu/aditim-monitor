"""API для работы с планами стадий задач для компонентов инструмента"""

from .api_client import ApiClient


class ApiPlanTaskComponentStage(ApiClient):
    """API для работы с планами стадий задач для компонентов инструмента"""

    def get_plan_task_component_stage(self):
        """Получение всех планов стадий задач для компонентов"""
        return self._request("GET", "/api/plan_task_component_stage")

    def create_plan_task_component_stage(self, plan_stage_data):
        """Создание нового плана стадии"""
        return self._request("POST", "/api/plan_task_component_stage", json=plan_stage_data)
    
    def update_plan_task_component_stage(self, plan_stage_id, plan_stage_data):
        """Обновление плана стадии"""
        return self._request("PUT", f"/api/plan_task_component_stage/{plan_stage_id}", json=plan_stage_data)
    
    def delete_plan_task_component_stage(self, plan_stage_id):
        """Удаление плана стадии"""
        return self._request("DELETE", f"/api/plan_task_component_stage/{plan_stage_id}")

