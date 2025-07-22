"""
Менеджер справочников для ADITIM Monitor Client
Загружает все справочники один раз при запуске и предоставляет к ним доступ
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
        
        # Флаги загрузки
        self._departments_loaded = False
        self._profiles_loaded = False
        self._component_types_loaded = False
        self._statuses_loaded = False
        
        self._initialized = True
    
    def set_api_client(self, api_client: ApiClient):
        """Устанавливает клиент API"""
        self.api_client = api_client
    
    async def load_all_references(self):
        """Загрузка всех справочников асинхронно"""
        if not self.api_client:
            raise RuntimeError("API клиент не установлен")
        
        try:
            await self._load_departments()
            await self._load_profiles()  
            await self._load_component_types()
            await self._load_statuses()
            
        except Exception as e:
            raise
    
    def load_all_references_sync(self):
        """Синхронная загрузка всех справочников"""
        if not self.api_client:
            raise RuntimeError("API клиент не установлен")
        
        try:
            self._load_departments_sync()
            self._load_profiles_sync()
            self._load_component_types_sync()
            self._load_statuses_sync()
            
        except Exception as e:
            raise
    
    # Базовые методы загрузки
    def _load_departments_sync(self):
        """Синхронная загрузка департаментов"""
        try:
            departments = self.api_client.get_departments()
            self._departments = {dept['id']: dept['name'] for dept in departments}
            self._departments_loaded = True
        except Exception as e:
            pass
    
    async def _load_departments(self):
        """Загружает справочник департаментов"""
        try:
            departments = self.api_client.get_departments()
            self._departments = {dept['id']: dept['name'] for dept in departments}
            self._departments_loaded = True
        except Exception as e:
            raise
    
    def _load_profiles_sync(self):
        """Синхронная загрузка профилей"""
        try:
            profiles = self.api_client.get_profiles()
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
    
    async def _load_profiles(self):
        """Загружает справочник профилей"""
        try:
            profiles = self.api_client.get_profiles()
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
            raise
    
    def _load_component_types_core(self):
        """Базовая логика загрузки типов компонентов"""
        try:
            component_types = self.api_client.get_component_types()
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
    
    async def _load_component_types(self):
        """Загружает справочник типов компонентов"""
        self._load_component_types_core()
    
    def _load_statuses_core(self):
        """Базовая логика загрузки статусов компонентов"""
        try:
            if not self.api_client:
                raise RuntimeError("API клиент не установлен")
            
            # Загружаем статусы компонентов из API
            statuses = self.api_client.get_component_statuses()
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
    
    async def _load_statuses(self):
        """Загружает справочник статусов"""
        try:
            self._load_statuses_core()
        except Exception as e:
            raise
    
    def load_profile_dimensions(self, profile_id: int) -> List[str]:
        """Загружает размерности для конкретного профиля по его ID"""
        if profile_id in self._profile_dimensions:
            return self._profile_dimensions[profile_id]
        
        try:
            # Вызываем API для получения размерностей
            dimensions = self.api_client.get_profile_dimensions(profile_id)
            # Кешируем результат
            self._profile_dimensions[profile_id] = dimensions
            return dimensions
        except Exception as e:
            return []
    
    def load_tool_dimensions(self) -> List[Dict[str, Any]]:
        """Загружает справочник размерностей инструментов"""
        try:
            response = self.api_client.get_tool_dimensions()
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
    
    def get_profiles(self) -> Dict[int, Dict[str, str]]:
        """Возвращает словарь профилей {id: {article, description, sketch}}"""
        return self._profiles.copy()
    
    def get_profile(self, profile_id: int) -> Optional[Dict[str, str]]:
        """Возвращает данные одного профиля по ID"""
        return self._profiles.get(profile_id)
    
    def get_component_types(self) -> Dict[int, Dict[str, str]]:
        """Возвращает словарь типов компонентов {id: {name, description}}"""
        return self._component_types.copy()
    
    def get_statuses(self) -> Dict[int, str]:
        """Возвращает словарь статусов компонентов {id: name}"""
        return self._statuses.copy()
    
    def get_default_status_id(self) -> int:
        """Возвращает ID статуса компонента по умолчанию ('в разработке')"""
        return 1  # ID статуса "в разработке"
    
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
    
    def refresh_references(self):
        """Принудительное обновление всех справочников"""
        self._departments_loaded = False
        self._profiles_loaded = False
        self._component_types_loaded = False
        self._statuses_loaded = False
        self._profile_dimensions.clear()
        
        self.load_all_references_sync()

# Глобальный экземпляр менеджера справочников
references_manager = ReferencesManager()
