"""
Синхронный HTTP-клиент для взаимодействия с сервером ADITIM Monitor
"""

import httpx
from typing import List, Optional, Dict, Any
from .constants import API_BASE_URL, API_TIMEOUT


class ApiClient:
    """Синхронный HTTP-клиент для взаимодействия с сервером"""
    
    def __init__(self, base_url: str = API_BASE_URL):
        """Инициализация клиента API"""
        self.base_url = base_url
        self.timeout = API_TIMEOUT
        
    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[Any, Any]:
        """Выполнение HTTP-запроса к серверу"""
        url = f"{self.base_url}{endpoint}"
        
        with httpx.Client(timeout=self.timeout) as client:
            response = client.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
    
    # === Операции с задачами ===
    def get_tasks(
        self, 
        status_id: Optional[int] = None,
        department_id: Optional[int] = None,
        limit: Optional[int] = None
    ) -> List[Dict[Any, Any]]:
        """Получение списка задач с фильтрацией"""
        params = {}
        if status_id:
            params["status_id"] = status_id
        if department_id:
            params["department_id"] = department_id
        if limit:
            params["limit"] = limit
            
        return self._request("GET", "/api/tasks/", params=params)
    
    def update_task(self, task_id: int, task_data: Dict[str, Any]) -> Dict[Any, Any]:
        """Обновление задачи"""
        return self._request("PUT", f"/api/tasks/{task_id}", json=task_data)
    
    def delete_task(self, task_id: int) -> Dict[Any, Any]:
        """Удаление задачи"""
        return self._request("DELETE", f"/api/tasks/{task_id}")
    
    def update_task_position(self, task_id: int, new_position: int) -> Dict[Any, Any]:
        """Обновление позиции задачи в очереди"""
        return self._request("PUT", f"/api/tasks/{task_id}/position", 
                           json={"position": new_position})
    
    # === Справочники ===
    def get_departments(self) -> List[Dict[Any, Any]]:
        """Получение всех подразделений"""
        return self._request("GET", "/api/directories/dir_department")
    
    def get_statuses(self) -> List[Dict[Any, Any]]:
        """Получение всех статусов задач"""
        return self._request("GET", "/api/directories/dir_task_status")
    
    def get_component_statuses(self) -> List[Dict[Any, Any]]:
        """Получение всех статусов компонентов"""
        return self._request("GET", "/api/directories/dir_component_status")
    
    def get_component_types(self) -> List[Dict[Any, Any]]:
        """Получение типов компонентов"""
        try:
            return self._request("GET", "/api/directories/dir_component_type")
        except Exception:
            return []
    
    def get_profile_dimensions(self, profile_id: int) -> List[str]:
        """Получение доступных размеров профиля"""
        try:
            response = self._request("GET", "/api/directories/dir_tool_dimension")
            
            if isinstance(response, list):
                return [item['name'] for item in response if 'name' in item]
            elif isinstance(response, dict) and response.get('success'):
                return [item['name'] for item in response.get('data', []) if 'name' in item]
                
        except Exception:
            pass
            
        return ['40x20', '50x30', '60x40', '25x15']
    
    def get_tool_dimensions(self) -> Dict[str, Any]:
        """Получение размеров инструментов из справочников"""
        try:
            data = self._request("GET", "/api/directories/dir_tool_dimension")
            
            if isinstance(data, list):
                return {'success': True, 'data': data}
            elif isinstance(data, dict):
                return data
                
        except Exception:
            pass
            
        return {'success': False, 'data': []}
    
    # === Профили ===
    def get_profile(self) -> List[Dict[Any, Any]]:
        """Получение всех профилей"""
        return self._request("GET", "/api/profile")

    def create_profile(self, profile_data: Dict[str, Any]) -> Dict[Any, Any]:
        """Создание нового профиля"""
        return self._request("POST", "/api/profile", json=profile_data)
    
    def delete_profile(self, profile_id: int) -> Dict[Any, Any]:
        """Удаление профиля по ID"""
        return self._request("DELETE", f"/api/profile/{profile_id}")

    def get_profile_sketch(self, profile_id: int) -> Dict[str, Any]:
        """Получение эскиза профиля"""
        try:
            return self._request("GET", f"/api/profile/{profile_id}/sketch")
        except Exception:
            return {}
    
    # === Инструменты профиля ===
    def get_profile_tool(self) -> List[Dict[Any, Any]]:
        """Получение всех инструментов профиля"""
        return self._request("GET", "/api/profile-tool")

    def create_profile_tool(self, tool_data: Dict[str, Any]) -> Dict[Any, Any]:
        """Создание нового инструмента профиля"""
        return self._request("POST", "/api/profile-tool", json=tool_data)

    def delete_profile_tool_by_profile(self, profile_id: int) -> Dict[Any, Any]:
        """Удаление всех инструментов, связанных с профилем"""
        return self._request("DELETE", f"/api/profile-tool/by-profile/{profile_id}")

    def get_profile_tool_component(self, tool_id: int) -> List[Dict[Any, Any]]:
        """Получение компонентов инструмента профиля"""
        return self._request("GET", f"/api/profile-tool/{tool_id}/component")

    def create_profile_tool_component(self, tool_id: int, component_data: Dict[str, Any]) -> Dict[Any, Any]:
        """Создание компонента инструмента профиля"""
        return self._request("POST", f"/api/profile-tool/{tool_id}/component", json=component_data)

    def delete_profile_tool_component(self, tool_id: int) -> Dict[Any, Any]:
        """Удаление всех компонентов инструмента профиля"""
        return self._request("DELETE", f"/api/profile-tool/{tool_id}/component")
    
    # === Продукты ===
    def get_product(self) -> List[Dict[Any, Any]]:
        """Получение всех продуктов"""
        return self._request("GET", "/api/product")

    def create_product(self, product_data: Dict[str, Any]) -> Dict[Any, Any]:
        """Создание нового продукта"""
        return self._request("POST", "/api/product", json=product_data)
    
    def get_product_component(self, product_id: int) -> List[Dict[Any, Any]]:
        """Получение компонентов продукта"""
        return self._request("GET", f"/api/product/{product_id}/component")

    def create_product_component(self, product_id: int, component_data: Dict[str, Any]) -> Dict[Any, Any]:
        """Создание компонента продукта"""
        return self._request("POST", f"/api/product/{product_id}/component", json=component_data)