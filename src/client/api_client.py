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
        return self._request("GET", "/api/directories/statuses")
    
    def get_type_works(self) -> List[Dict[Any, Any]]:
        """Get all work types"""
        return self._request("GET", "/api/directories/work_types")
    
    # Profile operations
    def get_profiles(self) -> List[Dict[Any, Any]]:
        """Get all profiles"""
        return self._request("GET", "/api/profiles")
    
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
