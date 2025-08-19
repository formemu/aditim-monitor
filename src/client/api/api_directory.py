"""
API для работы со справочниками
"""

from .api_client import ApiClient
from typing import List, Dict, Any


class ApiDirectory(ApiClient):
    """API для справочников"""
    
    def get_department(self):
        """Получение всех подразделений"""
        return self._request("GET", "/api/directory/dir_department")
    
    def get_component_status(self):
        """Получение всех статусов компонентов"""
        return self._request("GET", "/api/directory/dir_component_status")

    def get_component_type(self):
        """Получение типов компонентов"""
        return self._request("GET", "/api/directory/dir_component_type")

    def get_tool_dimension(self):
        """Получение размерностей инструментов"""
        return self._request("GET", "/api/directory/dir_tool_dimension")

    def get_task_status(self):
        """Получение статусов задач"""
        return self._request("GET", "/api/directory/dir_task_status")