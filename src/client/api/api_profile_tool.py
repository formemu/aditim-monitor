"""
API для работы с инструментами профиля
"""

from .api_client import ApiClient
from typing import List, Dict, Any


class ApiProfileTool(ApiClient):
    """API для инструментов профиля"""
    
    def get_profile_tool(self) -> List[Dict[Any, Any]]:
        """Получение всех инструментов профиля"""
        return self._request("GET", "/api/profile-tool")
    
    def create_profile_tool(self, tool_data: Dict[str, Any]) -> Dict[Any, Any]:
        """Создание нового инструмента профиля"""
        return self._request("POST", "/api/profile-tool", json=tool_data)

    def delete_profile_tool(self, tool_id: int) -> None:
        """Удаление инструмента профиля"""
        self._request("DELETE", f"/api/profile-tool/{tool_id}")



    def get_profile_tool_component(self, tool_id: int) -> List[Dict[Any, Any]]:
        """Получение компонентов инструмента профиля"""
        return self._request("GET", f"/api/profile-tool/{tool_id}/component")

    def create_profile_tool_component(self, tool_id: int, component_data: Dict[str, Any]) -> Dict[Any, Any]:
        """Создание компонента инструмента профиля"""
        return self._request("POST", f"/api/profile-tool/{tool_id}/component", json=component_data)

    def delete_profile_tool_component(self, tool_id: int) -> None:
        """Удаление компонента инструмента профиля"""
        self._request("DELETE", f"/api/profile-tool/{tool_id}/component")