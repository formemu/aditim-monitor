"""API для работы с инструментами профиля"""
from .api_client import ApiClient



class ApiProfileTool(ApiClient):
    """API для инструментов профиля"""
    
    def get_profile_tool(self):
        """Получение всех инструментов профиля"""
        return self._request("GET", "/api/profile-tool")

    def create_profile_tool(self, tool_data):
        """Создание нового инструмента профиля"""
        return self._request("POST", "/api/profile-tool", json=tool_data)

    def update_profile_tool(self, tool_id, tool_data):
        """Обновление существующего инструмента профиля"""
        return self._request("PATCH", f"/api/profile-tool/{tool_id}", json=tool_data)

    def delete_profile_tool(self, tool_id):
        """Удаление инструмента профиля"""
        self._request("DELETE", f"/api/profile-tool/{tool_id}")

    def get_profile_tool_component(self, tool_id):
        """Получение компонентов инструмента профиля"""
        return self._request("GET", f"/api/profile-tool/{tool_id}/component")

    def create_profile_tool_component(self, tool_id, component_data):
        """Создание компонента инструмента профиля"""
        return self._request("POST", f"/api/profile-tool/{tool_id}/component", json=component_data)

    def delete_profile_tool_component(self, tool_id):
        """Удаление компонента инструмента профиля"""
        self._request("DELETE", f"/api/profile-tool/{tool_id}/component")

    def delete_profile_tool_component_by_id(self, component_id):
        """Удаление конкретного компонента по ID"""
        self._request("DELETE", f"/api/profile-tool-component/{component_id}")