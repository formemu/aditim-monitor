"""
Менеджер справочников для ADITIM Monitor Client
Загружает все справочники один раз при запуске и предоставляет к ним доступ
Поддерживает асинхронное обновление справочников во время работы
"""

from typing import Dict, List, Any, Optional
from .api_client import ApiClient


class ReferencesManager:
    """Менеджер справочников с однократной загрузкой при запуске"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.initialized = False
        return cls._instance
    
    def __init__(self):
        if self.initialized:
            return
            
        self.api_client = None
        
        # Справочники
        self.department = {}          # {id: name}
        self.profile = {}             # {id: {article, description, sketch}}
        self.component_type = {}      # {id: {name, description}}
        self.profile_dimension = {}   # {profile_id: [dimensions]}
        self.status = {}            # {id: name} - статусы компонентов
        self.profile_tool = {}       # {id: {profile_id, dimension_id, description}}
        self.product = {}            # {id: {name, description, department_id}}
        self.task_status = {}       # {id: name} - статусы задач
        self.dimension = {}         # {id:  dimension} размерность

        # Флаги загрузки
        self.department_loaded = False
        self.profile_loaded = False
        self.component_type_loaded = False
        self.status_loaded = False
        self.profile_tool_loaded = False
        self.product_loaded = False
        self.task_status_loaded = False
        self.dimension_loaded = False

        self.initialized = True
    
    def set_api_client(self, api_client: ApiClient):
        """Устанавливает клиент API"""
        self.api_client = api_client
    
    def load_all_references_sync(self):
        """Синхронная загрузка всех справочников"""
        if not self.api_client:
            raise RuntimeError("API клиент не установлен")
        
        try:
            self.load_department_sync()
            self.load_profile_sync()
            self.load_component_type_sync()
            self.load_status_sync()
            self.load_profile_tool_sync()
            self.load_product_sync()
            self.load_task_status_sync()
            self.load_dimension_sync()

        except Exception as e:
            raise
    
    # Базовые методы загрузки
    def load_department_sync(self):
        """Синхронная загрузка департаментов"""
        try:
            department = self.api_client.get_department()
            self.department = {dept['id']: dept['name'] for dept in department}
            self.department_loaded = True
        except Exception as e:
            self.department_loaded = False
    
    def load_profile_sync(self):
        """Синхронная загрузка профилей"""
        try:
            profiles = self.api_client.get_profile()
            self.profile = {
                profile['id']: {
                    'article': profile['article'],
                    'description': profile.get('description', ''),
                    'sketch': profile.get('sketch')
                } 
                for profile in profiles
            }
            self.profile_loaded = True
        except Exception as e:
            self.profile_loaded = False

    def load_component_type_sync(self):
        """Синхронная загрузка типов компонентов"""
        try:
            component_types = self.api_client.get_component_type()
            self.component_type = {
                comp_type['id']: {
                    'name': comp_type['name'],
                    'description': comp_type.get('description', '')
                }
                for comp_type in component_types
            }
            self.component_type_loaded = True
        except Exception as e:
            self.component_type_loaded = False
    

    def load_status_sync(self):
        """Синхронная загрузка статусов"""
        try:
            if not self.api_client:
                raise RuntimeError("API клиент не установлен")
            # Загружаем статусы компонентов из API
            status = self.api_client.get_component_status()
            self.status = {status['id']: status['name'] for status in status}
            self.status_loaded = True
        except Exception as e:
            self.status_loaded = False

    def load_profile_tool_sync(self):
        """Синхронная загрузка инструментов профилей"""
        try:
            profile_tools = self.api_client.get_profile_tool()
            self.profile_tools = {
                tool['id']: {
                    'profile_id': tool['profile_id'],
                    'dimension_id': tool.get('dimension_id'),
                    'description': tool.get('description', '')
                }
                for tool in profile_tools
            }
            self.profile_tool_loaded = True
        except Exception as e:
            self.profile_tool_loaded = False

    def load_product_sync(self):
        """Синхронная загрузка изделий"""
        try:
            product = self.api_client.get_product()
            self.product = {
                product['id']: {
                    'name': product['name'],
                    'description': product.get('description', ''),
                    'department_id': product.get('department_id')
                }
                for product in product
            }
            self.product_loaded = True
        except Exception as e:
            self.product_loaded = False

    def load_task_status_sync(self):
        """Синхронная загрузка статусов задач"""
        try:
            task_status = self.api_client.get_task_status()
            self.task_status = {status['id']: status['name'] for status in task_status}
            self.task_status_loaded = True
        except Exception as e:
            self.task_status_loaded = False
    
    
    def load_dimension_sync(self):
        """Синхронная загрузка размерностей инструментов"""
        try:
            response = self.api_client.get_tool_dimension()
            dimension = response['data']
            self.dimension = {
                dim['id']: {
                    'dimension': dim['dimension'],
                    'description': dim.get('description', '')
                }
                for dim in dimension
            }
            self.dimension_loaded = True
        except Exception as e:
            self.dimension_loaded = False

    # Геттеры
    def get_department(self) -> Dict[int, str]:
        """Возвращает словарь департаментов {id: name}"""
        return self.department.copy()
    
    def get_profile(self) -> Dict[int, Dict[str, str]]:
        """Возвращает словарь профилей {id: {article, description, sketch}}"""
        return self.profile.copy()
       
    def get_component_type(self) -> Dict[int, Dict[str, str]]:
        """Возвращает словарь типов компонентов {id: {name, description}}"""
        return self.component_type.copy()
    
    def get_status(self) -> Dict[int, str]:
        """Возвращает словарь статусов компонентов {id: name}"""
        return self.status.copy()
    
    def get_component_status(self, status_id: int) -> Optional[Dict[str, str]]:
        """Возвращает данные одного статуса компонента по ID"""
        status_name = self.status.get(status_id)
        if status_name:
            return {"id": status_id, "name": status_name}
        return None
    
    def get_default_status_id(self) -> int:
        """Возвращает ID статуса компонента по умолчанию ('в разработке')"""
        return 1  # ID статуса "в разработке"

    def get_profile_tool(self) -> Dict[int, Dict[str, Any]]:
        """Возвращает словарь инструментов профилей {id: {profile_id, dimension_id, description}}"""
        return self.profile_tools.copy()


    def get_product_by_id(self) -> Dict[int, Dict[str, Any]]:
        """Возвращает словарь изделий {id: {name, description, department_id}}"""
        return self.product.copy()

    def get_product(self, product_id: int) -> Optional[Dict[str, Any]]:
        """Возвращает данные одного изделия по ID"""
        return self.product.get(product_id)

    def get_task_status(self) -> Dict[int, str]:
        """Возвращает словарь статусов задач {id: name}"""
        return self.task_status.copy()

    def get_dimension(self) -> Dict[int, str]:
        """Возвращает словарь размерностей {id: name}"""
        return self.dimension.copy()
    
    def get_component_type_by_id(self, type_id: int) -> Optional[Dict[str, str]]:
        """Возвращает данные одного типа компонента по ID"""
        return self.component_type.get(type_id)

    def get_task_status_by_id(self, status_id: int) -> Optional[Dict[str, str]]:
        """Возвращает данные одного статуса задачи по ID"""
        status_name = self.task_status.get(status_id)
        if status_name:
            return {"id": status_id, "name": status_name}
        return None
    
    def get_profile_tool_by_id(self, tool_id: int) -> Optional[Dict[str, Any]]:
        """Возвращает данные одного инструмента профиля по ID"""
        return self.profile_tools.get(tool_id)
    
    def get_profile_by_id(self, profile_id: int) -> Optional[Dict[str, str]]:
        """Возвращает данные одного профиля по ID"""
        return self.profile.get(profile_id)

    # Обновление справочников
    def refresh_department_async(self):
        """Асинхронное обновление справочника департаментов"""
        from .async_util import run_async
        
        def _refresh():
            self.department_loaded = False
            self.load_department_sync()
            return self.department
        
        run_async(
            _refresh,
            on_success=lambda result: print("✅ Департаменты обновлены"),
            on_error=lambda error: print(f"❌ Ошибка обновления департаментов: {error}")
        )
    
    def refresh_profile_async(self):
        """Асинхронное обновление справочника профилей"""
        from .async_util import run_async
        
        def _refresh():
            self.profile_loaded = False
            self.load_profile_sync()
            return self.profile
        
        run_async(
            _refresh,
            on_success=lambda result: print("✅ Профили обновлены"),
            on_error=lambda error: print(f"❌ Ошибка обновления профилей: {error}")
        )
    

    def refresh_references_async(self):
        """Асинхронное принудительное обновление всех справочников"""
        from .async_util import run_async
        
        def _refresh_sync():
            self.department_loaded = False
            self.profile_loaded = False
            self.component_type_loaded = False
            self.status_loaded = False
            self.profile_tool_loaded = False
            self.product_loaded = False
            self.task_status_loaded = False
            self.profile_dimension.clear()
            
            self.load_all_references_sync()
            return True
        
        # Запускаем обновление асинхронно
        run_async(
            _refresh_sync,
            on_success=lambda result: print("✅ Справочники обновлены асинхронно"),
            on_error=lambda error: print(f"❌ Ошибка обновления справочников: {error}")
        )

    def search_profile(self, query: str) -> List[Dict[str, Any]]:
        """Поиск профилей ТОЛЬКО по артикулу"""
        if not query or len(query) < 2:
            return []
        
        query_lower = query.lower()
        results = []
        
        for profile_id, profile_data in self.profile.items():
            article = profile_data.get('article', '').lower()
            
            # Поиск только по артикулу
            if query_lower in article:
                results.append({
                    'id': profile_id,
                    'article': profile_data.get('article', ''),
                    'description': profile_data.get('description', ''),
                    'sketch': profile_data.get('sketch')
                })
        
        return results
    
# Глобальный экземпляр менеджера справочников
references_manager = ReferencesManager()
