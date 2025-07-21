"""
Менеджер справочников для ADITIM Monitor Client
Загружает все справочники один раз при запуске и предоставляет к ним доступ
"""

from typing import Dict, List, Any, Optional
from .api_client import ApiClient


class ReferencesManager:
    """Менеджер справочников с однократной загрузкой при запуске"""
    
    _instance = None  # Singleton pattern
    
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
        """Устанавливает API клиент для загрузки данных"""
        self.api_client = api_client
    
    async def load_all_references(self):
        """Загружает все справочники асинхронно"""
        if not self.api_client:
            raise RuntimeError("API клиент не установлен")
        
        try:
            # Загружаем все справочники параллельно
            await self._load_departments()
            await self._load_profiles()
            await self._load_component_types()
            await self._load_statuses()
            
            print("✅ Все справочники успешно загружены")
            
        except Exception as e:
            print(f"❌ Ошибка загрузки справочников: {e}")
            raise
    
    def load_all_references_sync(self):
        """Синхронная загрузка всех справочников"""
        if not self.api_client:
            raise RuntimeError("API клиент не установлен")
        
        try:
            # Загружаем все справочники синхронно
            self._load_departments_sync()
            self._load_profiles_sync()
            self._load_component_types_sync()
            self._load_statuses_sync()
            
            print("✅ Все справочники успешно загружены")
            
        except Exception as e:
            print(f"❌ Ошибка загрузки справочников: {e}")
            raise
    
    async def _load_departments(self):
        """Загружает справочник департаментов"""
        try:
            departments = self.api_client.get_departments()
            self._departments = {dept['id']: dept['name'] for dept in departments}
            self._departments_loaded = True
            print(f"📁 Загружено департаментов: {len(self._departments)}")
        except Exception as e:
            print(f"❌ Ошибка загрузки департаментов: {e}")
            raise
    
    def _load_departments_sync(self):
        """Синхронная загрузка департаментов"""
        try:
            departments = self.api_client.get_departments()
            self._departments = {dept['id']: dept['name'] for dept in departments}
            self._departments_loaded = True
            print(f"📁 Загружено департаментов: {len(self._departments)}")
        except Exception as e:
            print(f"❌ Ошибка загрузки департаментов: {e}")
            raise
    
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
            print(f"🔧 Загружено профилей: {len(self._profiles)}")
        except Exception as e:
            print(f"❌ Ошибка загрузки профилей: {e}")
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
            print(f"🔧 Загружено профилей: {len(self._profiles)}")
        except Exception as e:
            print(f"❌ Ошибка загрузки профилей: {e}")
            raise
    
    async def _load_component_types(self):
        """Загружает справочник типов компонентов"""
        try:
            # Предполагаем что есть метод get_component_types
            component_types = self.api_client.get_component_types()
            self._component_types = {
                comp_type['id']: {
                    'name': comp_type['name'],
                    'description': comp_type.get('description', '')
                }
                for comp_type in component_types
            }
            self._component_types_loaded = True
            print(f"⚙️ Загружено типов компонентов: {len(self._component_types)}")
        except Exception as e:
            print(f"❌ Ошибка загрузки типов компонентов: {e}")
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
        try:
            # Предполагаем что есть метод get_component_types
            component_types = self.api_client.get_component_types()
            self._component_types = {
                comp_type['id']: {
                    'name': comp_type['name'],
                    'description': comp_type.get('description', '')
                }
                for comp_type in component_types
            }
            self._component_types_loaded = True
            print(f"⚙️ Загружено типов компонентов: {len(self._component_types)}")
        except Exception as e:
            print(f"❌ Ошибка загрузки типов компонентов: {e}")
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
    
    async def _load_statuses(self):
        """Загружает справочник статусов"""
        try:
            # Пока создаем статичный справочник статусов
            self._statuses = {
                1: 'В разработке',
                2: 'Готово',
                3: 'На проверке',
                4: 'Отклонено',
                5: 'В производстве'
            }
            self._statuses_loaded = True
            print(f"📋 Загружено статусов: {len(self._statuses)}")
        except Exception as e:
            print(f"❌ Ошибка загрузки статусов: {e}")
            raise
    
    def _load_statuses_sync(self):
        """Синхронная загрузка статусов"""
        try:
            # Пока создаем статичный справочник статусов
            self._statuses = {
                1: 'В разработке',
                2: 'Готово',
                3: 'На проверке',
                4: 'Отклонено',
                5: 'В производстве'
            }
            self._statuses_loaded = True
            print(f"📋 Загружено статусов: {len(self._statuses)}")
        except Exception as e:
            print(f"❌ Ошибка загрузки статусов: {e}")
            raise
    
    def load_profile_dimensions(self, profile_id: int) -> List[str]:
        """Загружает размерности для конкретного профиля (с кэшированием)"""
        if profile_id in self._profile_dimensions:
            return self._profile_dimensions[profile_id]
        
        try:
            # Предполагаем что есть метод get_profile_dimensions
            dimensions = self.api_client.get_profile_dimensions(profile_id)
            self._profile_dimensions[profile_id] = dimensions
            return dimensions
        except Exception as e:
            print(f"❌ Ошибка загрузки размерностей для профиля {profile_id}: {e}")
            # Возвращаем заглушку
            default_dimensions = ['40x20', '50x30', '60x40', '25x15']
            self._profile_dimensions[profile_id] = default_dimensions
            return default_dimensions
    
    # Методы доступа к справочникам
    
    def get_departments(self) -> Dict[int, str]:
        """Возвращает справочник департаментов"""
        if not self._departments_loaded:
            print("⚠️ Департаменты еще не загружены")
            return {}
        return self._departments.copy()
    
    def get_department_name(self, dept_id: int) -> str:
        """Возвращает название департамента по ID"""
        return self._departments.get(dept_id, f"ID: {dept_id}")
    
    def get_profiles(self) -> Dict[int, Dict[str, Any]]:
        """Возвращает справочник профилей"""
        if not self._profiles_loaded:
            print("⚠️ Профили еще не загружены")
            return {}
        return self._profiles.copy()
    
    def get_profile(self, profile_id: int) -> Optional[Dict[str, Any]]:
        """Возвращает данные конкретного профиля"""
        return self._profiles.get(profile_id)
    
    def search_profiles(self, query: str) -> List[Dict[str, Any]]:
        """Поиск профилей по артикулу или описанию"""
        if not self._profiles_loaded:
            return []
        
        query = query.lower()
        results = []
        
        for profile_id, profile_data in self._profiles.items():
            if (query in profile_data['article'].lower() or 
                query in profile_data.get('description', '').lower()):
                results.append({
                    'id': profile_id,
                    **profile_data
                })
        
        return results
    
    def get_component_types(self) -> Dict[int, Dict[str, str]]:
        """Возвращает справочник типов компонентов"""
        if not self._component_types_loaded:
            print("⚠️ Типы компонентов еще не загружены")
            return {}
        return self._component_types.copy()
    
    def get_component_type_name(self, type_id: int) -> str:
        """Возвращает название типа компонента по ID"""
        component_type = self._component_types.get(type_id, {})
        return component_type.get('name', f"ID: {type_id}")
    
    def get_statuses(self) -> Dict[int, str]:
        """Возвращает справочник статусов"""
        if not self._statuses_loaded:
            print("⚠️ Статусы еще не загружены")
            return {}
        return self._statuses.copy()
    
    def get_default_status_id(self) -> int:
        """Возвращает ID статуса по умолчанию ('В разработке')"""
        for status_id, status_name in self._statuses.items():
            if status_name == 'В разработке':
                return status_id
        return 1  # Fallback
    
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
