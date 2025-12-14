"""Мастер создания задачи"""
from PySide6.QtWidgets import QWizard
from PySide6.QtCore import QFile, QDate
from PySide6.QtUiTools import QUiLoader
from ...constant import UI_PATHS_ABS, get_style_path
from ...api_manager import api_manager
from ...style_util import load_styles
from .page_profiletool_selection import PageProfiletoolSelection
from .page_profiletool_component_dev import PageProfiletoolComponentDev
from .page_profiletool_component_prod import PageProfiletoolComponentProd
from .page_profiletool_component_rev import PageProfiletoolComponentRev
from .page_profiletool_blank import PageProfiletoolBlank

# Константы
PAGE = {
    "START": 0,
    "PROFILETOOL_SELECTION": 1,
    "PROFILETOOL_COMPONENT_DEV": 2,
    "PROFILETOOL_COMPONENT_SELECTION": 3,
    "PROFILETOOL_COMPONENT_REV": 4,
    "PROFILETOOL_BLANK": 5,
    "PRODUCT_SELECTION": 6,
    "PRODUCT_COMPONENT_SELECTION": 7,
    "TASK_DETAIL": 8
}

class WizardTaskCreate(QWizard):
    """Мастер создания задачи"""
    def __init__(self, parent=None):
        super().__init__(parent)
        # Состояние
        self.profileTool = None
        self.product = None
        self.task_data = {
            "status_id": 1,
            "created": QDate.currentDate().toString("yyyy-MM-dd"),
            "component": list()
        }
        self.load_ui()
        
        # Инициализация страниц
        self.page_profiletool_selection = PageProfiletoolSelection(self, self.ui)
        self.page_profiletool_component_dev = PageProfiletoolComponentDev(self, self.ui)
        self.page_profiletool_component_prod = PageProfiletoolComponentProd(self, self.ui)
        self.page_profiletool_component_rev = PageProfiletoolComponentRev(self, self.ui)
        self.page_profiletool_blank = PageProfiletoolBlank(self, self.ui)
        
        self.setup_ui()
        self.setWizardStyle(QWizard.WizardStyle.ClassicStyle)
    
    def load_ui(self):
        """Загрузка UI из файла"""
        ui_file = QFile(UI_PATHS_ABS["WIZARD_TASK_CREATE"])
        ui_file.open(QFile.ReadOnly)
        loader = QUiLoader()
        self.ui = loader.load(ui_file)
        ui_file.close()

    def setup_ui(self):
        """Настраивает логику визарда."""
        self.setStyleSheet(load_styles(get_style_path("WIZARDS")))
        self.addPage(self.ui.wizardPage_start)
        self.addPage(self.ui.wizardPage_profiletool_selection)
        self.addPage(self.ui.wizardPage_profiletool_component_dev)
        self.addPage(self.ui.wizardPage_profiletool_component_selection)
        self.addPage(self.ui.wizardPage_profiletool_component_rev)
        self.addPage(self.ui.wizardPage_profiletool_blank)
        self.addPage(self.ui.wizardPage_product_selection)
        self.addPage(self.ui.wizardPage_product_component_selection)
        self.addPage(self.ui.wizardPage_task_detail)
        self.currentIdChanged.connect(self.on_page_changed)
        self.setStartId(0)

        self.ui.dateEdit_date.setDate(QDate.currentDate().addDays(14))
        
        self.load_comboBox_task_type()

    def on_page_changed(self, id: int):
        """Обработчик изменения текущей страницы"""
        if id == PAGE["START"]:
            pass
        elif id == PAGE["PROFILETOOL_COMPONENT_DEV"]:
            self.page_profiletool_component_dev.load()
        elif id == PAGE["PROFILETOOL_COMPONENT_SELECTION"]:
            self.page_profiletool_component_prod.load()
        elif id == PAGE["PROFILETOOL_COMPONENT_REV"]:
            self.page_profiletool_component_rev.load()
        elif id == PAGE["PROFILETOOL_BLANK"]:
            self.page_profiletool_blank.load()
        elif id == PAGE["TASK_DETAIL"]:
            self.task_data["type_id"] = self.ui.comboBox_work_type.currentIndex()
            self.create_list_profiletool_component_selected()

    def nextId(self):
        """Переопределяем маршрут переходов между страницами."""
        if self.currentId() == PAGE["START"]:
            if self.ui.comboBox_product_type.currentIndex() == 0:
                return PAGE["PROFILETOOL_SELECTION"]
            else:
                return PAGE["PRODUCT_SELECTION"]
        elif self.currentId() == PAGE["PROFILETOOL_SELECTION"]:
            if self.ui.comboBox_work_type.currentIndex() == 0:
                return PAGE["PROFILETOOL_COMPONENT_DEV"]
            elif self.ui.comboBox_work_type.currentIndex() == 1:
                return PAGE["PROFILETOOL_COMPONENT_SELECTION"]
            elif self.ui.comboBox_work_type.currentIndex() == 2:
                return PAGE["PROFILETOOL_COMPONENT_REV"]
            elif self.ui.comboBox_work_type.currentIndex() == 3:
                return PAGE["PROFILETOOL_BLANK"]
        elif self.currentId() == PAGE["PROFILETOOL_COMPONENT_DEV"]:
            return PAGE["TASK_DETAIL"]
        elif self.currentId() == PAGE["PROFILETOOL_COMPONENT_REV"]:
            return PAGE["TASK_DETAIL"]  
        elif self.currentId() == PAGE["PROFILETOOL_COMPONENT_SELECTION"]:
            return PAGE["TASK_DETAIL"]
        elif self.currentId() == PAGE["PROFILETOOL_BLANK"]:
            return PAGE["TASK_DETAIL"]
        elif self.currentId() == PAGE["PRODUCT_SELECTION"]:
            return PAGE["PRODUCT_COMPONENT_SELECTION"]
        elif self.currentId() == PAGE["PRODUCT_COMPONENT_SELECTION"]:
            return PAGE["TASK_DETAIL"]
        elif self.currentId() == PAGE["TASK_DETAIL"]:
            return -1
        return 0

    # --- Страница выбора типа изделия ---
    def load_comboBox_task_type(self):
        """запонляет выбор типа работ"""
        for type in api_manager.directory['task_type']:
            self.ui.comboBox_work_type.addItem(type['name'], type['id'])

    def create_list_profiletool_component_selected(self):
        """Получает выбранные компоненты из страниц"""
        # Для задач с заготовками компоненты обрабатываются отдельно
        if self.task_data['type_id'] == 3:
            return
        
        # Получаем компоненты через страницы
        if self.task_data['type_id'] == 0:
            selected_components = self.page_profiletool_component_dev.get_selected_component()
        elif self.task_data['type_id'] == 1:
            selected_components = self.page_profiletool_component_prod.get_selected_component()
        elif self.task_data['type_id'] == 2:
            selected_components = self.page_profiletool_component_rev.get_selected_component()
        else:
            selected_components = []
        
        self.task_data["component"] = selected_components

    # --- Создание задач ---
    def accept(self):
        self.task_data['description'] = self.ui.textEdit_description.toPlainText()
        self.task_data['deadline'] = self.ui.dateEdit_date.date().toString("yyyy-MM-dd")
        self.task_data['created'] = QDate.currentDate().toString("yyyy-MM-dd")
        if self.task_data["profiletool_id"]:
            if self.task_data['type_id'] == 0:
                # Проверка для задачи "Разработка"
                if not self.validate_profiletool_exists():
                    return
                self.create_profiletool_task_dev()
            elif self.task_data['type_id'] == 1:
                # Проверка для задачи "Изготовление"
                if not self.validate_profiletool_exists():
                    return
                self.create_profiletool_task_prod()
            elif self.task_data['type_id'] == 2:
                # Проверка для задачи "Изменение"
                if not self.validate_profiletool_exists():
                    return
                self.create_profiletool_task_rev()
            elif self.task_data['type_id'] == 3:
                # Проверяем наличие инструмента и компонентов
                if not self.validate_profiletool_exists():
                    return  # Не создаем задачу, если нет инструмента или компонентов
                # Проверяем наличие заготовок перед созданием задачи
                if not self.validate_blank_availability():
                    return  # Не создаем задачу, если недостаточно заготовок
                self.create_profiletool_task_blank()
        elif self.task_data["product_id"]:
            self.create_product_task()
        super().accept()

    def create_profiletool_task_dev(self):
        task = api_manager.api_task.create_task(self.task_data)
        for component in self.task_data["component"]:
            component_data = {"profiletool_component_id": component['id']}
            api_manager.api_task.create_task_component(task['id'], component_data)


    def create_profiletool_task_prod(self):
        task = api_manager.api_task.create_task(self.task_data)
        for component in self.task_data["component"]:
            component_data = {"profiletool_component_id": component['id']}
            task_component = api_manager.api_task.create_task_component(task['id'], component_data)
            task_component_id = task_component['id']
            for selected_stage in component['stage']:
                stage = {
                    "work_subtype_id": selected_stage['work_subtype']['id'],
                    "stage_num": selected_stage['stage_num']
                }
                api_manager.api_task.create_task_component_stage(task_component_id, stage)

    def create_profiletool_task_rev(self):
        task = api_manager.api_task.create_task(self.task_data)
        for component in self.task_data["component"]:
            component_data = {"profiletool_component_id": component['id']}
            api_manager.api_task.create_task_component(task['id'], component_data)

    def validate_profiletool_exists(self):
        """Проверка наличия инструмента и его компонентов перед созданием задачи"""
        from PySide6.QtWidgets import QMessageBox
        
        # Проверяем, что инструмент выбран
        if not self.profileTool:
            QMessageBox.warning(
                self,
                "Ошибка",
                "Инструмент не выбран!\n\n"
                "Выберите инструмент профиля для создания задачи."
            )
            return False
        
        # Проверяем, что у инструмента есть компоненты
        list_component = self.profileTool.get('component', [])
        if not list_component or len(list_component) == 0:
            profile_article = self.task_data.get('profile', {}).get('article', 'N/A')
            dimension_name = self.profileTool.get('dimension', {}).get('name', 'N/A')
            
            # Определяем тип задачи для сообщения
            task_type_names = {
                0: "разработку",
                1: "изготовление",
                2: "изменение",
                3: "изготовление заготовок"
            }
            task_type = task_type_names.get(self.task_data.get('type_id', 3), "выполнение работ")
            
            QMessageBox.warning(
                self,
                "Ошибка: нет компонентов инструмента",
                f"У инструмента профиля '{profile_article}' (размерность {dimension_name}) "
                f"отсутствуют компоненты!\n\n"
                f"Невозможно создать задачу на {task_type}, "
                f"так как нет компонентов для работы.\n\n"
                f"Сначала создайте компоненты инструмента в разделе 'Профили'."
            )
            return False
        
        return True

    def validate_blank_availability(self):
        """Проверка достаточного количества заготовок для всех компонентов"""
        from PySide6.QtWidgets import QMessageBox
        
        # Получаем параметры заготовок через страницу
        blank_data_list = self.page_profiletool_blank.get_blank_data_list()
        
        # Получаем все компоненты профиля
        all_components = self.profileTool.get('component', []) if self.profileTool else []
        
        # Подсчитываем требуемое количество заготовок для каждого размера
        dict_required_blank = {}  # {(material_id, width, height, length): required_count}
        list_error_message = []
        
        # Получаем список компонентов, для которых выбраны заготовки
        dict_component_blank = {bd['component_id']: bd for bd in blank_data_list if bd}
        
        for component in all_components:
            component_id = component['id']
            
            # Если для компонента не выбрана заготовка
            if component_id not in dict_component_blank:
                # Пропускаем компоненты, у которых уже есть готовая заготовка
                # (они не отображаются в списке благодаря фильтрации в page_profiletool_blank.load())
                continue
            
            blank_data = dict_component_blank[component_id]
            list_blank = blank_data.get('list_blank', [])
            
            if not list_blank or len(list_blank) == 0:
                # Нет доступных заготовок
                component_name = component['type']['name']
                list_error_message.append(f"• Компонент '{component_name}': нет доступных заготовок")
                continue
            
            # Получаем параметры для идентификации размера
            first_blank = list_blank[0]
            material_id = first_blank.get('material', {}).get('id')
            width = first_blank.get('blank_width', 0)
            height = first_blank.get('blank_height', 0)
            length = first_blank.get('blank_length', 0)
            
            size_key = (material_id, width, height, length)
            
            # Требуется 1 заготовка на компонент
            if size_key not in dict_required_blank:
                dict_required_blank[size_key] = {
                    'required': 0,
                    'available': len(list_blank),
                    'material_name': first_blank.get('material', {}).get('name', 'Неизвестно'),
                    'size': f"{width}×{height}×{length}"
                }
            dict_required_blank[size_key]['required'] += 1
        
        # Проверяем, достаточно ли заготовок для каждого размера
        for size_key, data in dict_required_blank.items():
            if data['required'] > data['available']:
                list_error_message.append(
                    f"• {data['material_name']} {data['size']} мм: "
                    f"требуется {data['required']} шт, доступно {data['available']} шт"
                )
        
        # Если есть ошибки, показываем сообщение и не создаем задачу
        if list_error_message:
            error_text = "Невозможно создать задачу:\n\n" + "\n".join(list_error_message)
            QMessageBox.warning(self, "Недостаточно заготовок", error_text)
            return False
        
        return True

    def create_profiletool_task_blank(self):
        """Создание задачи для изготовления заготовок"""
        from PySide6.QtCore import QDate
        
        task = api_manager.api_task.create_task(self.task_data)
        
        # Получаем параметры заготовок через страницу
        blank_data_list = self.page_profiletool_blank.get_blank_data_list()
        
        # Словарь для отслеживания использованных заготовок по размеру
        dict_used_blank = {}  # {(material_id, width, height, length): [used_blank_ids]}
        
        for blank_data in blank_data_list:
            if not blank_data:
                continue  # Пропускаем, если заготовка не выбрана
            
            component_id = blank_data['component_id']
            list_blank = blank_data.get('list_blank', [])
            
            if not list_blank:
                continue  # Пропускаем, если нет доступных заготовок
            
            # Получаем параметры для идентификации размера
            first_blank = list_blank[0]
            material_id = first_blank.get('material', {}).get('id')
            width = first_blank.get('blank_width', 0)
            height = first_blank.get('blank_height', 0)
            length = first_blank.get('blank_length', 0)
            size_key = (material_id, width, height, length)
            
            # Инициализируем список использованных заготовок для этого размера
            if size_key not in dict_used_blank:
                dict_used_blank[size_key] = []
            
            # Ищем первую неиспользованную заготовку
            selected_blank = None
            for blank in list_blank:
                if blank['id'] not in dict_used_blank[size_key]:
                    selected_blank = blank
                    dict_used_blank[size_key].append(blank['id'])
                    break
            
            if not selected_blank:
                continue  # Нет доступных заготовок (все уже использованы)
            
            blank_id = selected_blank['id']
            
            # Создаем task_component
            component_data = {"profiletool_component_id": component_id}
            task_component = api_manager.api_task.create_task_component(task['id'], component_data)
            task_component_id = task_component['id']
            
            # Создаем этапы работ для заготовки (эрозионные и/или фрезерные)
            erosion_offset = blank_data.get('erosion_offset', 0.7)  # Получаем припуск из данных
            
            for work in blank_data.get('work', []):
                # Определяем номер этапа в зависимости от типа работы
                # ID 8 - эрозионные работы (этап 1)
                # ID 9 - фрезерные работы (этап 2)
                if work['id'] == 8:
                    stage_num = 1  # Эрозионные работы
                    # Добавляем описание с информацией о припуске для эрозионных работ
                    description = f"Припуск на обработку: {erosion_offset} мм"
                elif work['id'] == 9:
                    stage_num = 2  # Фрезерные работы
                    description = None
                else:
                    stage_num = 1  # По умолчанию
                    description = None
                
                stage_data = {
                    "work_subtype_id": work['id'],
                    "stage_num": stage_num
                }
                
                # Добавляем описание, если оно есть
                if description:
                    stage_data["description"] = description
                
                api_manager.api_task.create_task_component_stage(task_component_id, stage_data)
            
            # Обновляем ТОЛЬКО ОДНУ выбранную заготовку: привязываем к компоненту, добавляем размеры детали и дату изготовления
            blank_update_data = {
                "profiletool_component_id": component_id,
                "product_width": blank_data['product_width'],
                "product_height": blank_data['product_height'],
                "product_length": blank_data['product_length'],
                "date_product": QDate.currentDate().toString("yyyy-MM-dd")  # ← Устанавливаем дату изготовления
            }
            
            # Обновляем только выбранную заготовку
            api_manager.api_blank.update_blank(blank_id, blank_update_data)

