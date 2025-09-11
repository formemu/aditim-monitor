"""API для работы с планами стадий задач для компонентов инструмента"""

from .api_client import ApiClient


class ApiPlanTaskComponentStage(ApiClient):
    """API для работы с планами стадий задач для компонентов инструмента"""

    def get_plan_task_component_stage(self):
        """Получение всех планов стадий задач для компонентов"""
        return self._request("GET", "/api/plan_task_component_stage")

