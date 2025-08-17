"""API для работы с профилями"""
from .api_client import ApiClient


class ApiProfile(ApiClient):
    """API для профилей"""
    
    def get_profile(self):
        """Получение всех профилей"""
        return self._request("GET", "/api/profile")
    
    def create_profile(self, profile_data):
        """Создание нового профиля"""
        return self._request("POST", "/api/profile", json=profile_data)
    
    def update_profile(self, profile_id, profile_data):
        """Обновление существующего профиля"""
        return self._request("PUT", f"/api/profile/{profile_id}", json=profile_data)
    
    def delete_profile(self, profile_id):
        """Удаление профиля"""
        return self._request("DELETE", f"/api/profile/{profile_id}")