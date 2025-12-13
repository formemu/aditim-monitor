"""API для работы со справочниками"""

from .api_client import ApiClient

class ApiDirectory(ApiClient):
    """API для справочников"""
    
    def get_department(self):
        """Получение всех подразделений"""
        return self._request("GET", "/api/directory/dir_department")
    
    def get_component_status(self):
        """Получение всех статусов компонентов"""
        return self._request("GET", "/api/directory/dir_component_status")

    def get_component_type(self):
        """Получение типов компонентов"""
        return self._request("GET", "/api/directory/dir_component_type")

    def get_tool_dimension(self):
        """Получение размерностей инструментов"""
        return self._request("GET", "/api/directory/dir_tool_dimension")

    def get_task_status(self):
        """Получение статусов задач"""
        return self._request("GET", "/api/directory/dir_task_status")

    def get_machine(self):
        """Получение всех станков"""
        return self._request("GET", "/api/directory/dir_machine")

    def get_work_type(self):
        """Получение всех типов работ"""
        return self._request("GET", "/api/directory/dir_work_type")
    
    def get_work_subtype(self):
        """Получение всех подтипов работ"""
        return self._request("GET", "/api/directory/dir_work_subtype")

    def get_task_type(self):
        """Получение всех типов задач"""
        return self._request("GET", "/api/directory/dir_task_type")

    def get_task_location(self):
        """Получение всех местоположений задач"""
        return self._request("GET", "/api/directory/dir_task_location")

    def get_blank_material(self):
        """Получение всех материалов заготовок"""
        return self._request("GET", "/api/directory/dir_blank_material")

    def get_blank_type(self, material_id=None):
        """Получение всех типов заготовок с опциональным фильтром по материалу"""
        params = {}
        if material_id is not None:
            params['material_id'] = material_id
        return self._request("GET", "/api/directory/dir_blank_type", params=params)

    # =============================================================================
    # CRUD для размерностей инструментов (dir_profiletool_dimension)
    # =============================================================================
    def create_profiletool_dimension(self, dimension_data):
        """Создание новой размерности инструмента"""
        return self._request("POST", "/api/directory/dir_profiletool_dimension", json=dimension_data)
    
    def update_profiletool_dimension(self, dimension_id, dimension_data):
        """Обновление размерности инструмента"""
        return self._request("PUT", f"/api/directory/dir_profiletool_dimension/{dimension_id}", json=dimension_data)
    
    def delete_profiletool_dimension(self, dimension_id):
        """Удаление размерности инструмента"""
        return self._request("DELETE", f"/api/directory/dir_profiletool_dimension/{dimension_id}")

    # =============================================================================
    # CRUD для типов компонентов (dir_profiletool_component_type)
    # =============================================================================
    def create_component_type(self, component_type_data):
        """Создание нового типа компонента"""
        return self._request("POST", "/api/directory/dir_component_type", json=component_type_data)
    
    def update_component_type(self, component_type_id, component_type_data):
        """Обновление типа компонента"""
        return self._request("PUT", f"/api/directory/dir_component_type/{component_type_id}", json=component_type_data)
    
    def delete_component_type(self, component_type_id):
        """Удаление типа компонента"""
        return self._request("DELETE", f"/api/directory/dir_component_type/{component_type_id}")
