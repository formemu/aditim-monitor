"""Диалог редактирования описаний элементов задачи"""
from PySide6.QtWidgets import QDialog, QTreeWidgetItem, QLineEdit
from PySide6.QtCore import QFile, Qt
from PySide6.QtUiTools import QUiLoader
from ..constant import UI_PATHS_ABS
from ..api_manager import api_manager


class DialogEditDescriptions(QDialog):
    """Диалог для редактирования описаний компонентов, этапов и истории задачи"""
    
    def __init__(self, task, parent=None):
        super().__init__(parent)
        self.task = task
        self.changes = {}  # Словарь изменений: {entity_type: {id: new_description}}
        self.load_ui()
        self.setup_ui()
    
    def load_ui(self):
        """Загрузка UI из файла"""
        ui_file = QFile(UI_PATHS_ABS["DIALOG_EDIT_DESCRIPTIONS"])
        ui_file.open(QFile.ReadOnly)
        loader = QUiLoader()
        self.ui = loader.load(ui_file, self)
        ui_file.close()
    
    def setup_ui(self):
        """Настройка UI"""
        self.setWindowTitle(f"Редактирование описаний - Задача №{self.task['id']}")
        
        # Настройка дерева
        tree = self.ui.treeWidget_descriptions
        tree.setColumnWidth(0, 300)
        tree.setColumnWidth(1, 350)
        
        # Подключение кнопок
        self.ui.buttonBox.accepted.connect(self.save_changes)
        self.ui.buttonBox.rejected.connect(self.reject)
        
        # Загрузка данных
        self.load_descriptions()
    
    def load_descriptions(self):
        """Загрузка всех описаний из задачи"""
        tree = self.ui.treeWidget_descriptions
        tree.clear()
        
        # Инициализация структуры изменений
        self.changes = {
            'task': {},
            'component': {},
            'stage': {},
            'history': {}
        }
        
        # Корневой элемент - Задача
        root = QTreeWidgetItem(tree)
        root.setText(0, f"📋 Задача №{self.task['id']}")
        root.setExpanded(True)
        
        # Описание самой задачи
        task_desc_edit = self.create_description_edit(
            self.task.get('description', ''),
            'task',
            self.task['id']
        )
        task_desc_item = QTreeWidgetItem(root)
        task_desc_item.setText(0, "Описание задачи")
        tree.setItemWidget(task_desc_item, 1, task_desc_edit)
        
        # Компоненты
        if self.task.get('component'):
            components_item = QTreeWidgetItem(root)
            components_item.setText(0, f"📦 Компоненты ({len(self.task['component'])} шт)")
            components_item.setExpanded(True)
            
            for component in self.task['component']:
                self.add_component_item(components_item, component)
    
    def add_component_item(self, parent, component):
        """Добавляет компонент в дерево с возможностью редактирования описания"""
        tree = self.ui.treeWidget_descriptions
        
        # Получаем название компонента
        if component.get('profiletool_component_id'):
            comp_name = component['profiletool_component']['type']['name']
            comp_desc = component['profiletool_component'].get('description', '')
        elif component.get('product_component_id'):
            comp_name = component['product_component']['name']
            comp_desc = component['product_component'].get('description', '')
        else:
            comp_name = "Неизвестный компонент"
            comp_desc = ''
        
        comp_item = QTreeWidgetItem(parent)
        comp_item.setText(0, f"🔧 {comp_name}")
        comp_item.setExpanded(True)
        
        # Описание компонента (не редактируется здесь, т.к. это описание из profiletool_component)
        comp_desc_item = QTreeWidgetItem(comp_item)
        comp_desc_item.setText(0, "Описание компонента")
        comp_desc_item.setText(1, comp_desc or "(нет описания)")
        comp_desc_item.setForeground(1, Qt.gray)
        
        # Этапы работ (если есть)
        if component.get('stage'):
            stages_item = QTreeWidgetItem(comp_item)
            stages_item.setText(0, f"⚙️ Этапы работ ({len(component['stage'])} шт)")
            stages_item.setExpanded(True)
            
            for stage in component['stage']:
                self.add_stage_item(stages_item, stage)
        
        # История компонента (если это компонент профиля)
        if component.get('profiletool_component_id'):
            profiletool_comp = component['profiletool_component']
            if profiletool_comp.get('history'):
                history_item = QTreeWidgetItem(comp_item)
                history_item.setText(0, f"📜 История ({len(profiletool_comp['history'])} записей)")
                history_item.setExpanded(False)
                
                for hist in profiletool_comp['history']:
                    self.add_history_item(history_item, hist)
    
    def add_stage_item(self, parent, stage):
        """Добавляет этап работы с редактируемым описанием"""
        tree = self.ui.treeWidget_descriptions
        
        work_name = stage['work_subtype']['name'] if stage.get('work_subtype') else 'Неизвестная работа'
        stage_num = stage.get('stage_num', '?')
        
        stage_item = QTreeWidgetItem(parent)
        stage_item.setText(0, f"Этап {stage_num}: {work_name}")
        
        # Редактируемое описание этапа
        stage_desc_edit = self.create_description_edit(
            stage.get('description', ''),
            'stage',
            stage['id']
        )
        stage_desc_item = QTreeWidgetItem(stage_item)
        stage_desc_item.setText(0, "Описание этапа")
        tree.setItemWidget(stage_desc_item, 1, stage_desc_edit)
    
    def add_history_item(self, parent, history):
        """Добавляет запись истории с редактируемым описанием"""
        tree = self.ui.treeWidget_descriptions
        
        status_name = history['status']['name'] if history.get('status') else 'Неизвестный статус'
        date = history.get('date', '')
        
        hist_item = QTreeWidgetItem(parent)
        hist_item.setText(0, f"{date}: {status_name}")
        
        # Редактируемое описание записи истории
        hist_desc_edit = self.create_description_edit(
            history.get('description', ''),
            'history',
            history['id']
        )
        hist_desc_item = QTreeWidgetItem(hist_item)
        hist_desc_item.setText(0, "Описание")
        tree.setItemWidget(hist_desc_item, 1, hist_desc_edit)
    
    def create_description_edit(self, current_value, entity_type, entity_id):
        """Создает поле для редактирования описания"""
        edit = QLineEdit()
        edit.setPlaceholderText("Добавить описание...")
        edit.setText(current_value or '')
        
        # При изменении текста сохраняем в словарь изменений
        edit.textChanged.connect(
            lambda text: self.on_description_changed(entity_type, entity_id, text)
        )
        
        return edit
    
    def on_description_changed(self, entity_type, entity_id, new_text):
        """Обработчик изменения описания"""
        self.changes[entity_type][entity_id] = new_text
    
    def save_changes(self):
        """Сохранение всех изменений"""
        # Обновление описания задачи
        for task_id, description in self.changes['task'].items():
            api_manager.api_task.update_task(task_id, {'description': description})
        
        # Обновление описаний этапов
        for stage_id, description in self.changes['stage'].items():
            api_manager.api_task.update_task_component_stage(stage_id, {'description': description})
        
        # Обновление описаний истории
        for history_id, description in self.changes['history'].items():
            api_manager.api_profiletool.update_profiletool_component_history(
                history_id,
                {'description': description}
            )
        
        self.accept()
