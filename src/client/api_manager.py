"""
Менеджер справочников для ADITIM Monitor Client
Загружает все справочники один раз при запуске и предоставляет к ним доступ
Поддерживает асинхронное обновление справочников во время работы
"""

from .api.api_profile import ApiProfile
from .api.api_profile_tool import ApiProfileTool
from .api.api_product import ApiProduct
from .api.api_task import ApiTask
from .api.api_directory import ApiDirectory
from .api.api_plan import ApiPlanTaskComponentStage
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
        self.api_plan_task_component_stage = ApiPlanTaskComponentStage()


        # списки для хранения загруженных данных
        self.profile = []
        self.profile_tool = []
        self.product = []
        self.task = []
        self.queue = []

        # Словари для хранения загруженных справочников
        self.department = []
        self.component_type = []
        self.component_status = []
        self.task_status = []
        self.profile_tool_dimension = []
        self.machine = []

        #планы
        self.plan_task_component_stage = []

        # Флаги загрузки
        self.profile_loaded = False
        self.profile_tool_loaded = False
        self.product_loaded = False
        self.task_loaded = False
        self.queue_loaded = False

        self.department_loaded = False
        self.component_type_loaded = False
        self.component_status_loaded = False
        self.task_status_loaded = False
        self.profile_dimension_loaded = False
        self.machine_loaded = False

        self.plan_task_component_stage_loaded = False

        self.initialized = True

        self.load_all_directory()
        self.load_all_table()
        self.load_all_plan()

    def load_all_directory(self):
        self.load_department()
        self.load_component_type()
        self.load_component_status()
        self.load_task_status()
        self.load_profile_tool_dimension()
        self.load_machine()

    def load_all_plan(self):
        self.load_plan_task_component_stage()

    def load_all_table(self):
        self.load_profile()
        self.load_profile_tool()
        self.load_product()
        self.load_task()
        self.load_queue()


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

    def load_queue(self):
        """загрузка очереди"""
        try:
            self.queue = self.api_task.get_queue()
            self.queue_loaded = True
            print("данные о всех задачах в очереди обновились")
        except Exception as e:
            self.queue_loaded = False
            print("ошибка при загрузке очереди:", e)

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

    def load_plan_task_component_stage(self):
        """загрузка планов стадий задач для компонентов"""
        try:
            self.plan_task_component_stage = self.api_plan_task_component_stage.get_plan_task_component_stage()
            self.plan_task_component_stage_loaded = True
            print("данные о всех планах стадий задач для компонентов обновились")
        except Exception as e:
            self.plan_task_component_stage_loaded = False
            print("ошибка при загрузке планов стадий задач для компонентов:", e)

    def load_machine(self):
        """загрузка станков"""
        try:
            self.machine = self.api_directory.get_machine()
            self.machine_loaded = True
            print("данные о всех станках обновились")
        except Exception as e:
            self.machine_loaded = False
            print("ошибка при загрузке станков:", e)

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

    def refresh_machine_async(self):
        """Асинхронное обновление справочника станков"""
        def refresh():
            self.machine_loaded = False
            self.load_machine()
            return self.machine
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

    def refresh_plan_task_component_stage_async(self):
        """Асинхронное обновление таблицы планов стадий задач для компонентов"""
        def refresh():
            self.plan_task_component_stage_loaded = False
            self.load_plan_task_component_stage()
            return self.plan_task_component_stage
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

    def refresh_queue_async(self):
        """Асинхронное обновление таблицы очереди"""
        def refresh():
            self.queue_loaded = False
            self.load_queue()
            return self.queue
        run_async(refresh)

    def refresh_all_table_async(self):
        """Асинхронное обновление всех таблиц"""
        def refresh():
            self.load_all_table()
            return True
        run_async(refresh)

    # поиск по id
    def get_profile_by_id(self, id):
        """Поиск профиля по идентификатору"""
        try:
            profile_id = int(id)
            return next((p for p in self.profile if p['id'] == profile_id), None)
        except (ValueError, TypeError):
            return None

    def get_profile_tool_by_id(self, id):
        """Поиск инструмента профиля по идентификатору"""
        try:
            profile_tool_id = int(id)
            return next((pt for pt in self.profile_tool if pt['id'] == profile_tool_id), None)
        except (ValueError, TypeError):
            return None

    def get_product_by_id(self, id):
        """Поиск продукта по идентификатору"""
        try:
            product_id = int(id)
            return next((p for p in self.product if p['id'] == product_id), None)
        except (ValueError, TypeError):
            return None

    def get_task_by_id(self, id):
        try:
            task_id = int(id)
            return next((t for t in self.task if t['id'] == task_id), None)
        except (ValueError, TypeError):
            return None

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

    # манипуляции с задачами

    def add_to_queue(self, task):
        """Добавить задачу в очередь"""
        ApiTask.add_task_queue(task['id'])



# Глобальный экземпляр менеджера справочников
api_manager = ApiManager()
