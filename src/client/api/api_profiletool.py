"""API для работы с инструментами профиля"""
from .api_client import ApiClient



class ApiProfileTool(ApiClient):
    """API для инструментов профиля"""
    
    def get_profiletool(self):
        """Получение всех инструментов профиля"""
        return self._request("GET", "/api/profile-tool")

    def create_profiletool(self, tool_data):
        """Создание нового инструмента профиля"""
        return self._request("POST", "/api/profile-tool", json=tool_data)

    def update_profiletool(self, profiletool_id, tool_data):
        """Обновление существующего инструмента профиля"""
        return self._request("PATCH", f"/api/profile-tool/{profiletool_id}", json=tool_data)

    def delete_profiletool(self, profiletool_id):
        """Удаление инструмента профиля"""
        self._request("DELETE", f"/api/profile-tool/{profiletool_id}")

    def get_profiletool_component(self, profiletool_id):
        """Получение компонентов инструмента профиля"""
        return self._request("GET", f"/api/profile-tool/{profiletool_id}/component")
        

    def create_profiletool_component(self, profiletool_id, component_data):
        """Создание компонента инструмента профиля"""
        return self._request("POST", f"/api/profile-tool/{profiletool_id}/component", json=component_data)

    def delete_profiletool_component(self, profiletool_id):
        """Удаление компонентов инструмента профиля"""
        self._request("DELETE", f"/api/profile-tool/{profiletool_id}/component")

    def delete_profiletool_component_by_id(self, component_id):
        """Удаление конкретного компонента по ID"""
        self._request("DELETE", f"/api/profile-tool-component/{component_id}")

    def create_profiletool_component_history(self, profiletool_component_id, history_data):
        """Создание истории изменений компонента инструмента профиля"""
        return self._request("POST", f"/api/profile-tool-component/{profiletool_component_id}/history", json=history_data)