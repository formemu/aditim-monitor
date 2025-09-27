"""Менеджер данных для ADITIM Monitor Client"""
from PySide6.QtCore import QObject, Signal, QTimer
import asyncio
import websockets
from .async_util import run_async
from .api.api_profile import ApiProfile
from .api.api_profiletool import ApiProfileTool
from .api.api_product import ApiProduct
from .api.api_task import ApiTask
from .api.api_directory import ApiDirectory
from .api.api_plan import ApiPlanTaskComponentStage

class ApiManager(QObject):
    instance = None
    data_updated = Signal(str, str, bool)  # group, key, success

    def __new__(cls):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
            cls.instance.initialized = False
        return cls.instance

    def __init__(self):
        if getattr(self, 'initialized', False):
            return
            
        super().__init__()
        
        # API клиенты (сохраняем оригинальную структуру для обратной совместимости)
        self.api_profile = ApiProfile()
        self.api_profiletool = ApiProfileTool()
        self.api_product = ApiProduct()
        self.api_task = ApiTask()
        self.api_directory = ApiDirectory()
        self.api_plan_task_component_stage = ApiPlanTaskComponentStage()

        # Хранилища данных
        self.table = {}
        self.directory = {}
        self.plan = {}

        # Реестр данных
        self.registry = [
            # Таблицы
            ("profile", "table", self.api_profile.get_profile),
            ("profiletool", "table", self.api_profiletool.get_profiletool),
            ("product", "table", self.api_product.get_product),
            ("task", "table", self.api_task.get_task),
            ("queue", "table", self.api_task.get_queue),
            
            
            # Справочники
            ("department", "directory", self.api_directory.get_department),
            ("component_type", "directory", self.api_directory.get_component_type),
            ("component_status", "directory", self.api_directory.get_component_status),
            ("task_status", "directory", self.api_directory.get_task_status),
            ("profiletool_dimension", "directory", self.api_directory.get_tool_dimension),
            ("machine", "directory", self.api_directory.get_machine),
            ("work_type", "directory", self.api_directory.get_work_type),
            ("task_type", "directory", self.api_directory.get_task_type),
            ("task_location", "directory", self.api_directory.get_task_location),
            
            # Планы
            ("task_component_stage", "plan", self.api_plan_task_component_stage.get_plan_task_component_stage),
        ]

        # Инициализация хранилищ
        for key, group, _ in self.registry:
            getattr(self, group)[key] = []

        # Вебсокет
        self.ws_url = "ws://0.0.0.0:8000/ws/updates"
        self.websocket_task = None
        self.reconnect_delay = 5
        self.initialized = True

    def load_data(self, key: str, group: str, loader_func):
        """Загружает данные и испускает сигнал"""
        try:
            data = loader_func()
            getattr(self, group)[key] = data
            print(f"✅ Данные {group}['{key}'] обновлены")
            self.data_updated.emit(group, key, True)
        except Exception as e:
            print(f"❌ Ошибка загрузки {group}['{key}']: {e}")
            self.data_updated.emit(group, key, False)

    def start_websocket_listener(self):
        """Запускает прослушивание вебсокета"""
        if self.websocket_task and not self.websocket_task.done():
            return
        try:
            loop = asyncio.get_running_loop()
            self.websocket_task = loop.create_task(self.listen_loop())
        except RuntimeError:
            QTimer.singleShot(100, self.start_websocket_listener)

    async def listen_loop(self):
        """Цикл подключения вебсокета"""
        while True:
            try:
                async with websockets.connect(self.ws_url) as ws:
                    print(f"✅ [WebSocket] Подключено к {self.ws_url}")
                    await self.listen_to_connection(ws)
            except Exception as e:
                print(f"❌ [WebSocket] Ошибка: {e}")
                await asyncio.sleep(self.reconnect_delay)

    async def listen_to_connection(self, ws):
        """Прослушивание активного соединения"""
        try:
            async for message in ws:
                if data := self.parse_message(message):
                    QTimer.singleShot(0, lambda k=data["key"]: self.refresh(k))
        except websockets.ConnectionClosed:
            print("⚠️ [WebSocket] Соединение закрыто")
        except Exception as e:
            print(f"❌ [WebSocket] Ошибка: {e}")

    def parse_message(self, message):
        """Парсинг сообщения вебсокета"""
        try:
            data = eval(message) 
            return data if data.get("event") == "data_updated" else None
        except Exception as e:
            print(f"❌ [WebSocket] Ошибка парсинга: {e}")
            return None

    # Групповые загрузки
    def _load_group_async(self, target_group):
        """Загружает данные группы в фоне"""
        for key, group, loader in self.registry:
            if group == target_group:
                run_async(lambda k=key, g=group, l=loader: self.load_data(k, g, l))

    def load_all_async(self):
        """Загружает все данные в фоне"""
        self._load_group_async("table")
        self._load_group_async("directory")
        self._load_group_async("plan")

    # Обновление данных
    def refresh_async(self, key: str, group: str, loader_func):
        run_async(lambda: self.load_data(key, group, loader_func))

    def refresh(self, key: str):
        for k, group, loader in self.registry:
            if k == key:
                self.refresh_async(k, group, loader)
                return
        print(f"❌ Не найден источник: '{key}'")
    # Поиск
    def get_by_id(self, category: str, item_id) -> dict | None:
        for key, group, _ in self.registry:
            if key == category:
                data = getattr(self, group).get(key, [])
                try:
                    return next((item for item in data if item.get('id') == int(item_id)), None)
                except (ValueError, TypeError):
                    return None
        print(f"❌ Категория не найдена: '{category}'")
        return None

    def search_in(self, category: str, field: str, query: str) -> list:
        """Поиск элементов в категории по полю и запросу
        :param category: категория для поиска
        :param field: поле, в котором выполняется поиск
        :param query: строка запроса для поиска
        """
        for key, group, _ in self.registry:
            if key == category:
                data = getattr(self, group).get(key, [])
                query_lower = query.strip().lower()
                return [item for item in data if query_lower in str(item.get(field, "")).lower()]
        print(f"❌ Категория не найдена: '{category}'")
        return []
    
    def find_in(self, container, path: str, **kwargs) -> list:
        """
        Находит элементы в контейнере по пути и условиям.
        Автоматически приводит типы для сравнения (например, '123' == 123).
        
        :param container: dict, list или ORM-объект
        :param path: путь к вложенному списку, например "component.stage"
        :param kwargs: условия поиска, например id=52, machine_id=1
        :return: список найденных элементов
        """

        def is_equal(a, b):
            """Гибкое сравнение двух значений"""
            if a is None or b is None:
                return a is b  # только если оба None

            # Пробуем привести к одному типу
            if isinstance(a, str) and isinstance(b, (int, float)):
                try:
                    return float(a) == float(b)
                except ValueError:
                    return False
            elif isinstance(b, str) and isinstance(a, (int, float)):
                try:
                    return float(b) == float(a)
                except ValueError:
                    return False
            else:
                return a == b

        # Разбиваем путь
        keys = path.split('.')
        items = [container] if isinstance(container, dict) else container
        for key in keys:
            next_items = []
            for item in items:
                if isinstance(item, dict):
                    sub_items = item.get(key, [])
                    if isinstance(sub_items, list):
                        next_items.extend(sub_items)
                    elif sub_items is not None:
                        next_items.append(sub_items)
            items = next_items
            if not items:
                return []

        # Фильтруем по kwargs
        result = []
        for item in items:
            if isinstance(item, dict):
                match = True
                for k, v in kwargs.items():
                    value = item.get(k)
                    if not is_equal(value, v):
                        match = False
                        break
                if match:
                    result.append(item)

        return result

# Глобальный экземпляр
api_manager = ApiManager()