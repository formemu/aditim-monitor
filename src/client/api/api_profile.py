"""
API для работы с профилями
"""

from .api_client import ApiClient
from typing import List, Dict, Any


class ApiProfile(ApiClient):
    """API для профилей"""
    
    def get_profile(self) -> List[Dict[Any, Any]]:
        """Получение всех профилей"""
        return self._request("GET", "/api/profile")
    
    def create_profile(self, profile_data: Dict[str, Any]) -> Dict[Any, Any]:
        """Создание нового профиля"""
        return self._request("POST", "/api/profile", json=profile_data)
    
    def delete_profile(self, profile_id: int) -> Dict[Any, Any]:
        """Удаление профиля"""
        return self._request("DELETE", f"/api/profile/{profile_id}")