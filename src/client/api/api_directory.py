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
