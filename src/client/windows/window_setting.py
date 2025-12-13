"""Содержимое настроек для ADITIM Monitor Client"""
from PySide6.QtWidgets import QMessageBox, QDialog
from PySide6.QtCore import Qt

from ..base_window import BaseWindow
from ..base_table import BaseTable
from ..constant import UI_PATHS_ABS
from ..api_manager import api_manager
from ..widgets.setting.dialog_dimension import DialogDimension
from ..widgets.setting.dialog_component_type import DialogComponentType
from ..widgets.setting.dialog_plan_stage import DialogPlanStage


class WindowSetting(BaseWindow):
    """Виджет окна настроек для управления типами инструментов и их компонентами"""
    def __init__(self):
        self.dimension = None  # Выбранная размерность (тип инструмента)
        self.component_type = None  # Выбранный компонент
        self.plan_stage = None  # Выбранная стадия
        super().__init__(UI_PATHS_ABS["SETTING_CONTENT"], api_manager)

    # =============================================================================
    # ИНИЦИАЛИЗАЦИЯ И ЗАГРУЗКА ИНТЕРФЕЙСА
    # =============================================================================
    def setup_ui(self):
        """Настройка UI компонентов"""
        self.apply_styles()
        self.load_logo()

        # Подключение сигналов для размерностей (типов инструментов)
        self.ui.pushButton_dimension_add.clicked.connect(self.on_dimension_add_clicked)
        self.ui.pushButton_dimension_edit.clicked.connect(self.on_dimension_edit_clicked)
        self.ui.pushButton_dimension_delete.clicked.connect(self.on_dimension_delete_clicked)
        self.ui.tableWidget_dimension.itemClicked.connect(self.on_dimension_table_clicked)

        # Подключение сигналов для компонентов
        self.ui.pushButton_component_type_add.clicked.connect(self.on_component_type_add_clicked)
        self.ui.pushButton_component_type_edit.clicked.connect(self.on_component_type_edit_clicked)
        self.ui.pushButton_component_type_delete.clicked.connect(self.on_component_type_delete_clicked)
        self.ui.tableWidget_component_type.itemClicked.connect(self.on_component_type_table_clicked)

        # Подключение сигналов для стадий
        self.ui.pushButton_plan_stage_add.clicked.connect(self.on_plan_stage_add_clicked)
        self.ui.pushButton_plan_stage_edit.clicked.connect(self.on_plan_stage_edit_clicked)
        self.ui.pushButton_plan_stage_delete.clicked.connect(self.on_plan_stage_delete_clicked)
        self.ui.tableWidget_plan_stage.itemClicked.connect(self.on_plan_stage_table_clicked)

        self.refresh_data()

    # =============================================================================
    # УПРАВЛЕНИЕ ДАННЫМИ: ЗАГРУЗКА И ОБНОВЛЕНИЕ
    # =============================================================================
    def refresh_data(self):
        """Обновление данных в виджете"""
        self.dimension = None
        self.component_type = None
        self.plan_stage = None
        self.update_table_dimension()
        self.update_table_component_type()
        self.update_table_plan_stage()

    # =============================================================================
    # РАЗМЕРНОСТИ (ТИПЫ ИНСТРУМЕНТОВ): ТАБЛИЦА И ОБРАБОТЧИКИ
    # =============================================================================
    def update_table_dimension(self):
        """Обновление таблицы размерностей (типов инструментов)"""
        list_dimension = api_manager.directory.get('profiletool_dimension', [])
        
        BaseTable.populate_table(
            self.ui.tableWidget_dimension,
            ["Название", "Описание"],
            list_dimension,
            func_row_mapper=lambda d: [d['name'], d.get('description', '') or ''],
            func_id_getter=lambda d: d['id']
        )

    def on_dimension_table_clicked(self):
        """Обработчик выбора размерности в таблице"""
        dimension_id = BaseTable.get_selected_id(self.ui.tableWidget_dimension)
        self.dimension = api_manager.get_by_id('profiletool_dimension', dimension_id)
        # При выборе размерности обновляем компоненты
        self.component_type = None
        self.plan_stage = None
        self.update_table_component_type()
        self.update_table_plan_stage()

    def on_dimension_add_clicked(self):
        """Добавление нового типа инструмента"""
        dialog = DialogDimension(self)
        if dialog.exec() == QDialog.Accepted:
            dimension_data = dialog.get_dimension_data()
            try:
                api_manager.api_directory.create_profiletool_dimension(dimension_data)
                QMessageBox.information(self, "Успех", "Тип инструмента создан")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось создать тип инструмента: {str(e)}")

    def on_dimension_edit_clicked(self):
        """Редактирование типа инструмента"""
        if not self.dimension:
            QMessageBox.warning(self, "Внимание", "Выберите тип инструмента для редактирования")
            return
        
        dialog = DialogDimension(self, self.dimension)
        if dialog.exec() == QDialog.Accepted:
            dimension_data = dialog.get_dimension_data()
            try:
                api_manager.api_directory.update_profiletool_dimension(self.dimension['id'], dimension_data)
                QMessageBox.information(self, "Успех", "Тип инструмента обновлен")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось обновить тип инструмента: {str(e)}")

    def on_dimension_delete_clicked(self):
        """Удаление типа инструмента"""
        if not self.dimension:
            QMessageBox.warning(self, "Внимание", "Выберите тип инструмента для удаления")
            return
        
        reply = QMessageBox.question(
            self, 
            "Подтверждение", 
            f"Удалить тип инструмента '{self.dimension['name']}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                api_manager.api_directory.delete_profiletool_dimension(self.dimension['id'])
                QMessageBox.information(self, "Успех", "Тип инструмента удален")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось удалить тип инструмента: {str(e)}")

    # =============================================================================
    # КОМПОНЕНТЫ: ТАБЛИЦА И ОБРАБОТЧИКИ
    # =============================================================================
    def update_table_component_type(self):
        """Обновление таблицы типов компонентов"""
        list_component_type = api_manager.directory.get('profiletool_component_type', [])
        
        # Фильтрация по выбранному габариту
        dimension_id = BaseTable.get_selected_id(self.ui.tableWidget_dimension)
        if dimension_id:
            list_component_type = [
                ct for ct in list_component_type 
                if ct.get('profiletool_dimension_id') == dimension_id
            ]
        
        BaseTable.populate_table(
            self.ui.tableWidget_component_type,
            ["Название", "Ширина", "Высота", "Длина", "Описание"],
            list_component_type,
            func_row_mapper=lambda ct: [
                ct['name'],
                str(ct.get('width', '') or ''),
                str(ct.get('height', '') or ''),
                str(ct.get('length', '') or ''),
                ct.get('description', '') or ''
            ],
            func_id_getter=lambda ct: ct['id']
        )

    def on_component_type_table_clicked(self):
        """Обработчик выбора компонента в таблице"""
        component_type_id = BaseTable.get_selected_id(self.ui.tableWidget_component_type)
        self.component_type = api_manager.get_by_id('profiletool_component_type', component_type_id)
        # При выборе компонента обновляем стадии
        self.plan_stage = None
        self.update_table_plan_stage()

    def on_component_type_add_clicked(self):
        """Добавление нового компонента"""
        if not self.dimension:
            QMessageBox.warning(self, "Внимание", "Сначала выберите тип инструмента")
            return
        
        dialog = DialogComponentType(self, dimension_id=self.dimension['id'])
        if dialog.exec() == QDialog.Accepted:
            component_type_data = dialog.get_component_type_data()
            try:
                api_manager.api_directory.create_component_type(component_type_data)
                QMessageBox.information(self, "Успех", "Компонент создан")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось создать компонент: {str(e)}")

    def on_component_type_edit_clicked(self):
        """Редактирование компонента"""
        if not self.component_type:
            QMessageBox.warning(self, "Внимание", "Выберите компонент для редактирования")
            return
        
        dialog = DialogComponentType(self, self.component_type)
        if dialog.exec() == QDialog.Accepted:
            component_type_data = dialog.get_component_type_data()
            try:
                api_manager.api_directory.update_component_type(self.component_type['id'], component_type_data)
                QMessageBox.information(self, "Успех", "Компонент обновлен")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось обновить компонент: {str(e)}")

    def on_component_type_delete_clicked(self):
        """Удаление компонента"""
        if not self.component_type:
            QMessageBox.warning(self, "Внимание", "Выберите компонент для удаления")
            return
        
        reply = QMessageBox.question(
            self, 
            "Подтверждение", 
            f"Удалить компонент '{self.component_type['name']}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                api_manager.api_directory.delete_component_type(self.component_type['id'])
                QMessageBox.information(self, "Успех", "Компонент удален")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось удалить компонент: {str(e)}")

    # =============================================================================
    # СТАДИИ ИЗГОТОВЛЕНИЯ: ТАБЛИЦА И ОБРАБОТЧИКИ
    # =============================================================================
    def update_table_plan_stage(self):
        """Обновление таблицы стадий для выбранного компонента"""
        list_stage = api_manager.plan.get('task_component_stage', [])
        
        # Фильтрация по выбранному типу компонента
        component_type_id = BaseTable.get_selected_id(self.ui.tableWidget_component_type)
        if component_type_id:
            list_stage = [
                s for s in list_stage 
                if s.get('profiletool_component_type_id') == component_type_id
            ]
        
        # Сортируем по номеру стадии
        list_stage.sort(key=lambda x: x.get('stage_num', 0))
        
        # Маппер для получения имени работы
        def map_stage_row(stage):
            work_name = ""
            if stage.get('work_subtype_id'):
                work = api_manager.get_by_id('work_subtype', stage['work_subtype_id'])
                if work:
                    work_name = work['name']
            return [
                str(stage.get('stage_num', '') or ''),
                work_name,
                stage.get('description', '') or ''
            ]
        
        BaseTable.populate_table(
            self.ui.tableWidget_plan_stage,
            ["№", "Работа", "Описание"],
            list_stage,
            func_row_mapper=map_stage_row,
            func_id_getter=lambda s: s['id']
        )

    def on_plan_stage_table_clicked(self):
        """Обработчик выбора стадии в таблице"""
        plan_stage_id = BaseTable.get_selected_id(self.ui.tableWidget_plan_stage)
        self.plan_stage = api_manager.get_by_id('task_component_stage', plan_stage_id)

    def on_plan_stage_add_clicked(self):
        """Добавление новой стадии"""
        if not self.component_type:
            QMessageBox.warning(self, "Внимание", "Сначала выберите компонент")
            return
        
        dialog = DialogPlanStage(self, component_type=self.component_type)
        if dialog.exec() == QDialog.Accepted:
            plan_stage_data = dialog.get_plan_stage_data()
            try:
                api_manager.api_plan_task_component_stage.create_plan_task_component_stage(plan_stage_data)
                QMessageBox.information(self, "Успех", "Стадия создана")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось создать стадию: {str(e)}")

    def on_plan_stage_edit_clicked(self):
        """Редактирование стадии"""
        if not self.plan_stage:
            QMessageBox.warning(self, "Внимание", "Выберите стадию для редактирования")
            return
        
        dialog = DialogPlanStage(self, self.plan_stage, self.component_type)
        if dialog.exec() == QDialog.Accepted:
            plan_stage_data = dialog.get_plan_stage_data()
            try:
                api_manager.api_plan_task_component_stage.update_plan_task_component_stage(self.plan_stage['id'], plan_stage_data)
                QMessageBox.information(self, "Успех", "Стадия обновлена")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось обновить стадию: {str(e)}")

    def on_plan_stage_delete_clicked(self):
        """Удаление стадии"""
        if not self.plan_stage:
            QMessageBox.warning(self, "Внимание", "Выберите стадию для удаления")
            return
        
        reply = QMessageBox.question(
            self, 
            "Подтверждение", 
            f"Удалить стадию ID {self.plan_stage['id']}?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # TODO: Реализовать API удаления
            QMessageBox.information(self, "Информация", "Функция в разработке")
