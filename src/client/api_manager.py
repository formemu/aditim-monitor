"""
Менеджер справочников для ADITIM Monitor Client
Загружает все справочники один раз при запуске и предоставляет к ним доступ
Поддерживает асинхронное обновление справочников во время работы
"""

from .api.api_profile import ApiProfile
from .api.api_profile_tool import ApiProfileTool
from .api.api_product import ApiProduct
from .api.api_task import ApiTask
from.api.api_directory import ApiDirectory
from .async_util import run_async


class ApiManager:
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
        # Создаем экземпляры API-клиентов
        self.api_profile = ApiProfile()
        self.api_profile_tool = ApiProfileTool()
        self.api_product = ApiProduct()
        self.api_task = ApiTask()

        self.api_directory = ApiDirectory()


        # списки для хранения загруженных данных
        self.profile = []
        self.profile_tool = []
        self.product = []
        self.task = []

        # Словари для хранения загруженных справочников
        self.department = []
        self.component_type = []
        self.component_status = []
        self.task_status = []
        self.profile_tool_dimension = []

        # Флаги загрузки
        self.profile_loaded = False
        self.profile_tool_loaded = False
        self.product_loaded = False
        self.task_loaded = False

        self.department_loaded = False
        self.component_type_loaded = False
        self.component_status_loaded = False
        self.task_status_loaded = False
        self.profile_dimension_loaded = False

        self.initialized = True

        self.load_all_directory()
        self.load_all_table()

    def load_all_directory(self):
        self.load_department()
        self.load_component_type()
        self.load_component_status()
        self.load_task_status()
        self.load_profile_tool_dimension()

    def load_all_table(self):
        self.load_profile()
        self.load_profile_tool()
        self.load_product()
        self.load_task()


    # Базовые методы загрузки данных
    def load_profile(self):
        """загрузка профилей"""
        try:
            self.profile = self.api_profile.get_profile()
            self.profile_loaded = True
            print("данные о всех профилях обновились")
        except Exception as e:
            self.profile_loaded = False
            print("ошибка при загрузке профилей:", e)

    def load_profile_tool(self):
        """загрузка инструментов профилей"""
        try:
            self.profile_tool = self.api_profile_tool.get_profile_tool()
            self.profile_tool_loaded = True
            print("данные о всех инструментах профилей обновились")
        except Exception as e:
            self.profile_tool_loaded = False
            print("ошибка при загрузке инструментов профилей:", e)

    def load_profile_tool_component_by_id(self, item_id):
        """загрузка компонентов инструмента профилей"""
        try:
            return  self.api_profile_tool.get_profile_tool_component(item_id)
        except Exception as e:
            pass

    def load_product(self):
        """загрузка изделий"""
        try:
            self.product = self.api_product.get_product()
            self.product_loaded = True
            print("данные о всех изделиях обновились")
        except Exception as e:
            self.product_loaded = False
            print("ошибка при загрузке изделий:", e)

    def load_product_component_by_id(self, item_id):
        """загрузка компонентов изделий"""
        try:
            return self.api_product.get_product_component(item_id)
        except Exception as e:
            pass

    def load_task(self):
        """загрузка задач"""
        try:
            self.task = self.api_task.get_task()
            self.task_loaded = True
            print("данные о всех задачах обновились")
        except Exception as e:
            print("ошибка при загрузке задач:", e)
            self.task_loaded = False

    # Базовые методы загрузки справочников

    def load_department(self):
        """загрузка департаментов"""
        try:
            self.department = self.api_directory.get_department()
            self.department_loaded = True
            print("данные о всех департаментах обновились")
        except Exception as e:
            self.department_loaded = False
            print("ошибка при загрузке департаментов:", e)

    def load_component_type(self):
        """загрузка типов компонентов"""
        try:
            self.component_type = self.api_directory.get_component_type()
            self.component_type_loaded = True
            print("данные о всех типах компонентов обновились")
        except Exception as e:
            self.component_type_loaded = False
            print("ошибка при загрузке типов компонентов:", e)

    def load_component_status(self):
        """загрузка статусов"""
        try:
            self.component_status = self.api_directory.get_component_status()
            self.component_status_loaded = True
            print("данные о всех статусах компонентов обновились")
        except Exception as e:
            self.component_status_loaded = False
            print("ошибка при загрузке статусов компонентов:", e)

    def load_task_status(self):
        """загрузка статусов задач"""
        try:
            self.task_status = self.api_directory.get_task_status()
            self.task_status_loaded = True
            print("данные о всех статусах задач обновились")
        except Exception as e:
            self.task_status_loaded = False
            print("ошибка при загрузке статусов задач:", e)

    def load_profile_tool_dimension(self):
        """загрузка размерностей профилей"""
        try:
            self.profile_tool_dimension = self.api_directory.get_tool_dimension()
            self.profile_tool_dimension_loaded = True
            print("данные о всех размерностях профилей обновились")
        except Exception as e:
            self.profile_tool_dimension_loaded = False
            print("ошибка при загрузке размерностей профилей:", e)

    # асинхронное обновление справочников
    def refresh_department_async(self):
        """Асинхронное обновление справочника департаментов"""
        def refresh():
            self.department_loaded = False
            self.load_department()
            return self.department
        run_async(refresh)

    def refresh_component_type_async(self):
        """Асинхронное обновление справочника типов компонентов"""
        def refresh():
            self.component_type_loaded = False
            self.load_component_type()
            return self.component_type
        run_async(refresh)

    def refresh_component_status_async(self):
        """Асинхронное обновление справочника статусов"""
        def refresh():
            self.component_status_loaded = False
            self.load_component_status()
            return self.component_status
        run_async(refresh)

    def refresh_task_status_async(self):
        """Асинхронное обновление справочника статусов задач"""
        def refresh():
            self.task_status_loaded = False
            self.load_task_status()
            return self.task_status
        run_async(refresh)

    def refresh_profile_tool_dimension_async(self):
        """Асинхронное обновление справочника размерностей профилей"""
        def refresh():
            self.profile_tool_dimension_loaded = False
            self.load_profile_tool_dimension()
            return self.profile_tool_dimension
        run_async(refresh)

    def refresh_directory_async(self):
        """Асинхронное принудительное обновление всех справочников"""
        def refresh():
            self.department_loaded = False
            self.component_type_loaded = False
            self.component_status_loaded = False
            self.task_status_loaded = False
            self.profile_dimension_loaded = False
            self.load_all_directory()
            return True
        
        # Запускаем обновление асинхронно
        run_async(refresh)

    # асинхронное обновление данных таблиц
    def refresh_profile_async(self):
        """Асинхронное обновление таблицы профилей"""
        def refresh():
            self.profile_loaded = False
            self.load_profile()
            return self.profile
        run_async(refresh)

    def refresh_profile_tool_async(self):
        """Асинхронное обновление таблицы инструментов профилей"""
        def refresh():
            self.profile_tool_loaded = False
            self.load_profile_tool()
            return self.profile_tool
        run_async(refresh)

    def refresh_product_async(self):
        """Асинхронное обновление таблицы продуктов"""
        def refresh():
            self.product_loaded = False
            self.load_product()
            return self.product
        run_async(refresh)

    def refresh_task_async(self):
        """Асинхронное обновление таблицы задач"""
        def refresh():
            self.task_loaded = False
            self.load_task()
            return self.task
        run_async(refresh)

    def refresh_all_table_async(self):
        """Асинхронное обновление всех таблиц"""
        def refresh():
            self.load_all_table()
            return True
        run_async(refresh)

    # поиск по артикулу
    def get_profile_by_id(self, id):
        """Поиск профиля по артикулу"""
        return next((p for p in self.profile if p['id'] == id), None)

    def get_profile_tool_by_id(self, id):
        """Поиск инструмента профиля по идентификатору"""
        return next((pt for pt in self.profile_tool if pt['id'] == id), None)

    def get_product_by_id(self, id):
        """Поиск продукта по идентификатору"""
        return next((p for p in self.product if p['id'] == id), None)

    # Поиск профилей по артикулу
    def get_search_profile(self, find_article):
        """Поиск профилей по артикулу"""
        results = []
        for profile in self.profile:
            article = profile['article']
            if find_article in article:
                results.append(profile)       
        return results

    def get_search_product(self, find_name):
        """Поиск продуктов по имени"""
        results = []
        for product in self.product:
            name = product['name']
            if find_name in name:
                results.append(product)
        return results

# Глобальный экземпляр менеджера справочников
api_manager = ApiManager()
