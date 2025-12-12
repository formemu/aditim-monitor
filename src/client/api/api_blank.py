"""API клиент для работы с заготовками"""
from .api_client import ApiClient


class APIBlank(ApiClient):
    """Класс для работы с API заготовок"""
    
    def get_list_blank(self):
        """Получить список всех заготовок"""
        return self._request("GET", "/api/blank")
    
    def get_next_order_number(self):
        """Получить следующий номер заказа"""
        return self._request("GET", "/api/blank/order/next")
    
    def get_blank(self, blank_id: int):
        """Получить заготовку по ID"""
        return self._request("GET", f"/api/blank/{blank_id}")
    
    def create_blank(self, blank_data: dict):
        """Создать новую заготовку"""
        return self._request("POST", "/api/blank", json=blank_data)
    
    def create_list_blank(self, blank_data: dict, quantity: int):
        """Создать несколько заготовок одного типа
        
        Args:
            blank_data: Данные заготовки (material_id, component_id и т.д.)
            quantity: Количество заготовок для создания
        
        Returns:
            Список созданных заготовок, каждая с уникальным ID
        """
        data_with_quantity = {**blank_data, "quantity": quantity}
        return self._request("POST", "/api/blank/bulk", json=data_with_quantity)
    
    def update_blank(self, blank_id: int, blank_data: dict):
        """Обновить заготовку"""
        return self._request("PATCH", f"/api/blank/{blank_id}", json=blank_data)
    
    def delete_blank(self, blank_id: int):
        """Удалить заготовку"""
        return self._request("DELETE", f"/api/blank/{blank_id}")
