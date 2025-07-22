"""
Synchronous HTTP client for communication with ADITIM Monitor Server
"""

import httpx
from typing import List, Optional, Dict, Any
from .constants import API_BASE_URL, API_TIMEOUT


class ApiClient:
    """Synchronous HTTP client for server communication"""
    
    def __init__(self, base_url: str = API_BASE_URL):
        """Initialize API client"""
        self.base_url = base_url
        self.timeout = API_TIMEOUT
        
    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[Any, Any]:
        """Make HTTP request to server"""
        url = f"{self.base_url}{endpoint}"
        
        with httpx.Client(timeout=self.timeout) as client:
            response = client.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
    
    # Task operations
    def get_tasks(
        self, 
        status_id: Optional[int] = None,
        department_id: Optional[int] = None,
        limit: Optional[int] = None
    ) -> List[Dict[Any, Any]]:
        """Get tasks with optional filtering"""
        params = {}
        if status_id:
            params["status_id"] = status_id
        if department_id:
            params["department_id"] = department_id
        if limit:
            params["limit"] = limit
            
        return self._request("GET", "/api/tasks/", params=params)
    
    def update_task(self, task_id: int, task_data: Dict[str, Any]) -> Dict[Any, Any]:
        """Update task"""
        return self._request("PUT", f"/api/tasks/{task_id}", json=task_data)
    
    def delete_task(self, task_id: int) -> Dict[Any, Any]:
        """Delete task"""
        return self._request("DELETE", f"/api/tasks/{task_id}")
    
    def update_task_position(self, task_id: int, new_position: int) -> Dict[Any, Any]:
        """Update task position in queue"""
        return self._request("PUT", f"/api/tasks/{task_id}/position", 
                           json={"position": new_position})
    
    # Directory operations
    def get_departments(self) -> List[Dict[Any, Any]]:
        """Get all departments"""
        return self._request("GET", "/api/directories/departments")
    
    def get_statuses(self) -> List[Dict[Any, Any]]:
        """Get all task statuses"""
        return self._request("GET", "/api/directories/task-statuses")
    
    def get_component_statuses(self) -> List[Dict[Any, Any]]:
        """Get all component statuses"""
        return self._request("GET", "/api/directories/component-statuses")
    
    # Profile operations
    def get_profiles(self) -> List[Dict[Any, Any]]:
        """Get all profiles"""
        return self._request("GET", "/api/profiles")
    
    def create_profile(self, profile_data: Dict[str, Any]) -> Dict[Any, Any]:
        """Create new profile"""
        return self._request("POST", "/api/profiles", json=profile_data)
    
    def create_profile(self, profile_data: Dict[str, Any]) -> Dict[Any, Any]:
        """Create new profile"""
        return self._request("POST", "/api/profiles", json=profile_data)
    
    # Product operations  
    def get_products(self) -> List[Dict[Any, Any]]:
        """Get all products"""
        return self._request("GET", "/api/products")
    
    def create_product(self, product_data: Dict[str, Any]) -> Dict[Any, Any]:
        """Create new product"""
        return self._request("POST", "/api/products", json=product_data)
    
    def get_product_components(self, product_id: int) -> List[Dict[Any, Any]]:
        """Get components of a product"""
        return self._request("GET", f"/api/products/{product_id}/components")
    
    def create_product_component(self, product_id: int, component_data: Dict[str, Any]) -> Dict[Any, Any]:
        """Create new product component"""
        return self._request("POST", f"/api/products/{product_id}/components", json=component_data)
    
    # Profile Tools operations
    def get_profile_tools(self) -> List[Dict[Any, Any]]:
        """Get all profile tools"""
        return self._request("GET", "/api/profile-tools")
    
    def get_profile_tool_components(self, tool_id: int) -> List[Dict[Any, Any]]:
        """Get components of a profile tool"""
        return self._request("GET", f"/api/profile-tools/{tool_id}/components")
    
    # References operations (новые методы для справочников)
    def get_component_types(self) -> List[Dict[Any, Any]]:
        """Get all component types from dir_component_types"""
        try:
            return self._request("GET", "/api/directories/component-types")
        except Exception as e:
            # API method not implemented yet
            return []
    
    def get_profile_dimensions(self, profile_id: int) -> List[str]:
        """Get available dimensions for a profile"""
        try:
            # Получаем размерности из справочника размерностей инструментов
            dimensions_data = self._request("GET", "/api/directories/tool-dimensions")
            # API возвращает список словарей напрямую
            if isinstance(dimensions_data, list):
                return [dim['name'] for dim in dimensions_data if 'name' in dim]
            elif isinstance(dimensions_data, dict) and dimensions_data.get('success'):
                return [dim['name'] for dim in dimensions_data.get('data', []) if 'name' in dim]
            else:
                return ['40x20', '50x30', '60x40', '25x15']  # Default dimensions
        except Exception as e:
            # API method not implemented
            return ['40x20', '50x30', '60x40', '25x15']  # Default dimensions
    
    def get_profile_sketch(self, profile_id: int) -> Dict[str, Any]:
        """Get profile sketch data"""
        try:
            return self._request("GET", f"/api/profiles/{profile_id}/sketch")
        except Exception as e:
            # API method not implemented
            return {}
    
    def get_tool_dimensions(self) -> Dict[str, Any]:
        """Get tool dimensions from directories"""
        try:
            dimensions_data = self._request("GET", "/api/directories/tool-dimensions")
            # API возвращает список словарей напрямую
            if isinstance(dimensions_data, list):
                return {'success': True, 'data': dimensions_data}
            elif isinstance(dimensions_data, dict):
                return dimensions_data
            else:
                return {'success': False, 'data': []}
        except Exception as e:
            # API method not implemented
            return {'success': False, 'data': []}
    
    def create_profile_tool(self, tool_data: Dict[str, Any]) -> Dict[Any, Any]:
        """Create new profile tool"""
        return self._request("POST", "/api/profile-tools", json=tool_data)
    
    def create_profile_tool_component(self, tool_id: int, component_data: Dict[str, Any]) -> Dict[Any, Any]:
        """Create new profile tool component"""
        return self._request("POST", f"/api/profile-tools/{tool_id}/components", json=component_data)
