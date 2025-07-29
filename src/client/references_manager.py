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
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.api_client = None
        
        # Справочники
        self._departments = {}          # {id: name}
        self._profiles = {}             # {id: {article, description, sketch}}
        self._component_types = {}      # {id: {name, description}}
        self._profile_dimensions = {}   # {profile_id: [dimensions]}
        self._statuses = {}            # {id: name} - статусы компонентов
        self._profile_tools = {}       # {id: {profile_id, dimension_id, description}}
        self._products = {}            # {id: {name, description, department_id}}
        self._task_statuses = {}       # {id: name} - статусы задач
        
        # Флаги загрузки
        self._departments_loaded = False
        self._profiles_loaded = False
        self._component_types_loaded = False
        self._statuses_loaded = False
        self._profile_tools_loaded = False
        self._products_loaded = False
        self._task_statuses_loaded = False
        
        self._initialized = True
    
    def set_api_client(self, api_client: ApiClient):
        """Устанавливает клиент API"""
        self.api_client = api_client
    
    def load_all_references_sync(self):
        """Синхронная загрузка всех справочников"""
        if not self.api_client:
            raise RuntimeError("API клиент не установлен")
        
        try:
            self._load_departments_sync()
            self._load_profiles_sync()
            self._load_component_types_sync()
            self._load_statuses_sync()
            self._load_profile_tools_sync()
            self._load_products_sync()
            self._load_task_statuses_sync()
            
        except Exception as e:
            raise
    
    # Базовые методы загрузки
    def _load_departments_sync(self):
        """Синхронная загрузка департаментов"""
        try:
            departments = self.api_client.get_department()
            self._departments = {dept['id']: dept['name'] for dept in departments}
            self._departments_loaded = True
        except Exception as e:
            pass
    
    def _load_profiles_sync(self):
        """Синхронная загрузка профилей"""
        try:
            profiles = self.api_client.get_profile()
            self._profiles = {
                profile['id']: {
                    'article': profile['article'],
                    'description': profile.get('description', ''),
                    'sketch': profile.get('sketch')
                } 
                for profile in profiles
            }
            self._profiles_loaded = True
        except Exception as e:
            pass
    
    def _load_component_types_core(self):
        """Базовая логика загрузки типов компонентов"""
        try:
            component_types = self.api_client.get_component_type()
            self._component_types = {
                comp_type['id']: {
                    'name': comp_type['name'],
                    'description': comp_type.get('description', '')
                }
                for comp_type in component_types
            }
            self._component_types_loaded = True
        except Exception as e:
            # Если метода нет, создаем заглушку
            self._component_types = {
                1: {'name': 'Нож', 'description': 'Режущий элемент'},
                2: {'name': 'Направляющая', 'description': 'Направляющий элемент'},
                3: {'name': 'Калибр', 'description': 'Калибрующий элемент'},
                4: {'name': 'Плита формующая', 'description': 'Формующая плита'},
                5: {'name': 'Плита прижимная', 'description': 'Прижимная плита'},
                6: {'name': 'Втулка', 'description': 'Направляющая втулка'},
                7: {'name': 'Болт крепежный', 'description': 'Крепежный элемент'},
            }
            self._component_types_loaded = True
    
    def _load_component_types_sync(self):
        """Синхронная загрузка типов компонентов"""
        self._load_component_types_core()
    
    def _load_statuses_core(self):
        """Базовая логика загрузки статусов компонентов"""
        try:
            if not self.api_client:
                raise RuntimeError("API клиент не установлен")
            
            # Загружаем статусы компонентов из API
            statuses = self.api_client.get_component_status()
            self._statuses = {status['id']: status['name'] for status in statuses}
            self._statuses_loaded = True
            
        except Exception as e:
            # В случае ошибки используем захардкоженные значения из БД
            self._statuses = {
                1: 'в разработке',
                2: 'изготовление',
                3: 'на испытаниях', 
                4: 'в работе',
                5: 'не пошел',
                6: 'брак'
            }
            self._statuses_loaded = True
    
    def _load_statuses_sync(self):
        """Синхронная загрузка статусов"""
        try:
            self._load_statuses_core()
        except Exception as e:
            raise

    def _load_profile_tools_sync(self):
        """Синхронная загрузка инструментов профилей"""
        try:
            profile_tools = self.api_client.get_profile_tool()
            self._profile_tools = {
                tool['id']: {
                    'profile_id': tool['profile_id'],
                    'dimension_id': tool.get('dimension_id'),
                    'description': tool.get('description', '')
                }
                for tool in profile_tools
            }
            self._profile_tools_loaded = True
        except Exception as e:
            pass

    def _load_products_sync(self):
        """Синхронная загрузка изделий"""
        try:
            products = self.api_client.get_product()
            self._products = {
                product['id']: {
                    'name': product['name'],
                    'description': product.get('description', ''),
                    'department_id': product.get('department_id')
                }
                for product in products
            }
            self._products_loaded = True
        except Exception as e:
            pass

    def _load_task_statuses_sync(self):
        """Синхронная загрузка статусов задач"""
        try:
            task_statuses = self.api_client.get_task_status()
            self._task_statuses = {status['id']: status['name'] for status in task_statuses}
            self._task_statuses_loaded = True
        except Exception as e:
            # Захардкоженные статусы задач
            self._task_statuses = {
                1: 'В очереди',
                2: 'В работе',
                3: 'Выполнено',
                4: 'Отменено'
            }
            self._task_statuses_loaded = True
    
    def load_profile_dimensions(self, profile_id: int) -> List[str]:
        """Загружает размерности для конкретного профиля по его ID"""
        if profile_id in self._profile_dimensions:
            return self._profile_dimensions[profile_id]
        
        try:
            # Вызываем API для получения размерностей
            dimensions = self.api_client.get_profile_dimension(profile_id)
            # Кешируем результат
            self._profile_dimensions[profile_id] = dimensions
            return dimensions
        except Exception as e:
            return []
    
    def load_tool_dimensions(self) -> List[Dict[str, Any]]:
        """Загружает справочник размерностей инструментов"""
        try:
            response = self.api_client.get_tool_dimension()
            if response.get('success') and response.get('data'):
                dimensions = response.get('data', [])
                return dimensions
            else:
                return []
        except Exception as e:
            return []
    
    # Геттеры
    def get_departments(self) -> Dict[int, str]:
        """Возвращает словарь департаментов {id: name}"""
        return self._departments.copy()
    
    def get_profile(self) -> Dict[int, Dict[str, str]]:
        """Возвращает словарь профилей {id: {article, description, sketch}}"""
        return self._profiles.copy()
    
    def get_profile(self, profile_id: int) -> Optional[Dict[str, str]]:
        """Возвращает данные одного профиля по ID"""
        return self._profiles.get(profile_id)
    
    def get_component_types(self) -> Dict[int, Dict[str, str]]:
        """Возвращает словарь типов компонентов {id: {name, description}}"""
        return self._component_types.copy()
    
    def get_component_type(self, type_id: int) -> Optional[Dict[str, str]]:
        """Возвращает данные одного типа компонента по ID"""
        return self._component_types.get(type_id)
    
    def get_statuses(self) -> Dict[int, str]:
        """Возвращает словарь статусов компонентов {id: name}"""
        return self._statuses.copy()
    
    def get_component_status(self, status_id: int) -> Optional[Dict[str, str]]:
        """Возвращает данные одного статуса компонента по ID"""
        status_name = self._statuses.get(status_id)
        if status_name:
            return {"id": status_id, "name": status_name}
        return None
    
    def get_default_status_id(self) -> int:
        """Возвращает ID статуса компонента по умолчанию ('в разработке')"""
        return 1  # ID статуса "в разработке"

    def get_profile_tools(self) -> Dict[int, Dict[str, Any]]:
        """Возвращает словарь инструментов профилей {id: {profile_id, dimension_id, description}}"""
        return self._profile_tools.copy()

    def get_profile_tool(self, tool_id: int) -> Optional[Dict[str, Any]]:
        """Возвращает данные одного инструмента профиля по ID"""
        return self._profile_tools.get(tool_id)

    def get_products(self) -> Dict[int, Dict[str, Any]]:
        """Возвращает словарь изделий {id: {name, description, department_id}}"""
        return self._products.copy()

    def get_product(self, product_id: int) -> Optional[Dict[str, Any]]:
        """Возвращает данные одного изделия по ID"""
        return self._products.get(product_id)

    def get_task_statuses(self) -> Dict[int, str]:
        """Возвращает словарь статусов задач {id: name}"""
        return self._task_statuses.copy()

    def get_task_status(self, status_id: int) -> Optional[Dict[str, str]]:
        """Возвращает данные одного статуса задачи по ID"""
        status_name = self._task_statuses.get(status_id)
        if status_name:
            return {"id": status_id, "name": status_name}
        return None
    
    def refresh_departments_async(self):
        """Асинхронное обновление справочника департаментов"""
        from .async_util import run_async
        
        def _refresh():
            self._departments_loaded = False
            self._load_departments_sync()
            return self._departments
        
        run_async(
            _refresh,
            on_success=lambda result: print("✅ Департаменты обновлены"),
            on_error=lambda error: print(f"❌ Ошибка обновления департаментов: {error}")
        )
    
    def refresh_profiles_async(self):
        """Асинхронное обновление справочника профилей"""
        from .async_util import run_async
        
        def _refresh():
            self._profiles_loaded = False
            self._load_profiles_sync()
            return self._profiles
        
        run_async(
            _refresh,
            on_success=lambda result: print("✅ Профили обновлены"),
            on_error=lambda error: print(f"❌ Ошибка обновления профилей: {error}")
        )
    
    def search_profiles(self, query: str) -> List[Dict[str, Any]]:
        """Поиск профилей ТОЛЬКО по артикулу"""
        if not query or len(query) < 2:
            return []
        
        query_lower = query.lower()
        results = []
        
        for profile_id, profile_data in self._profiles.items():
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
    
    def refresh_references_async(self):
        """Асинхронное принудительное обновление всех справочников"""
        from .async_util import run_async
        
        def _refresh_sync():
            self._departments_loaded = False
            self._profiles_loaded = False
            self._component_types_loaded = False
            self._statuses_loaded = False
            self._profile_tools_loaded = False
            self._products_loaded = False
            self._task_statuses_loaded = False
            self._profile_dimensions.clear()
            
            self.load_all_references_sync()
            return True
        
        # Запускаем обновление асинхронно
        run_async(
            _refresh_sync,
            on_success=lambda result: print("✅ Справочники обновлены асинхронно"),
            on_error=lambda error: print(f"❌ Ошибка обновления справочников: {error}")
        )
    
    # def refresh_references(self): # НЕ ИСПОЛЬЗУЕТСЯ
    #     """Принудительное обновление всех справочников"""
    #     self._departments_loaded = False
    #     self._profiles_loaded = False
    #     self._component_types_loaded = False
    #     self._statuses_loaded = False
    #     self._profile_tools_loaded = False
    #     self._products_loaded = False
    #     self._task_statuses_loaded = False
    #     self._profile_dimensions.clear()
        
    #     self.load_all_references_sync()

# Глобальный экземпляр менеджера справочников
references_manager = ReferencesManager()
