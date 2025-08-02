"""
API для работы со справочниками
"""

from .api_client import ApiClient
from typing import List, Dict, Any


class ApiDirectory(ApiClient):
    """API для справочников"""
    
    def get_department(self) -> List[Dict[Any, Any]]:
        """Получение всех подразделений"""
        return self._request("GET", "/api/directory/dir_department")
    
    def get_status(self) -> List[Dict[Any, Any]]:
        """Получение всех статусов задач"""
        return self._request("GET", "/api/directory/dir_task_status")
    
    def get_component_status(self) -> List[Dict[Any, Any]]:
        """Получение всех статусов компонентов"""
        return self._request("GET", "/api/directory/dir_component_status")
    
    def get_component_type(self) -> List[Dict[Any, Any]]:
        """Получение типов компонентов"""
        return self._request("GET", "/api/directory/dir_component_type")