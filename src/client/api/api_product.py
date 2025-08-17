"""
API для работы с продуктами
"""

from .api_client import ApiClient


class ApiProduct(ApiClient):
    """API для продуктов"""
    
    def get_product(self):
        """Получение всех продуктов"""
        return self._request("GET", "/api/product")

    def create_product(self, product_data):
        """Создание нового продукта"""
        return self._request("POST", "/api/product", json=product_data)

    def update_product(self, product_id, product_data):
        """Обновление существующего продукта"""
        return self._request("PUT", f"/api/product/{product_id}", json=product_data)

    def get_product_component(self, product_id):
        """Получение компонентов продукта"""
        return self._request("GET", f"/api/product/{product_id}/component")

    def create_product_component(self, product_id, component_data):
        """Создание компонента продукта"""
        return self._request("POST", f"/api/product/{product_id}/component", json=component_data)

    def delete_product_component_by_id(self, component_id):
        """Удаление конкретного компонента по ID"""
        self._request("DELETE", f"/api/product-component/{component_id}")

    def delete_product(self, product_id):
        """Удаление продукта"""
        self._request("DELETE", f"/api/product/{product_id}")