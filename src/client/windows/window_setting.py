"""Содержимое настроек для ADITIM Monitor Client"""
from PySide6.QtWidgets import QWidget, QMessageBox, QTableWidgetItem, QDialog
from PySide6.QtCore import QFile, Qt
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QPixmap
from ..constant import UI_PATHS_ABS, ICON_PATHS_ABS, get_style_path
from ..api_manager import api_manager
from ..style_util import load_styles
from ..widgets.setting.dialog_dimension import DialogDimension
from ..widgets.setting.dialog_component_type import DialogComponentType
from ..widgets.setting.dialog_plan_stage import DialogPlanStage

class WindowSetting(QWidget):
    """Виджет окна настроек для управления типами инструментов и их компонентами"""
    def __init__(self):
        super().__init__()
        self.dimension = None  # Выбранная размерность (тип инструмента)
        self.component_type = None  # Выбранный компонент
        self.plan_stage = None  # Выбранная стадия
        self.load_ui()
        self.setup_ui()
        api_manager.data_updated.connect(self.refresh_data)

    # =============================================================================
    # ИНИЦИАЛИЗАЦИЯ И ЗАГРУЗКА ИНТЕРФЕЙСА
    # =============================================================================
    def load_ui(self):
        """Загрузка UI из файла"""
        ui_file = QFile(UI_PATHS_ABS["SETTING_CONTENT"])
        ui_file.open(QFile.ReadOnly)
        loader = QUiLoader()
        self.ui = loader.load(ui_file)
        ui_file.close()

    def setup_ui(self):
        """Настройка UI компонентов"""
        self.ui.setStyleSheet(load_styles(get_style_path("MAIN")))
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

    def load_logo(self):
        """Загрузка логотипа ADITIM"""
        logo_path = ICON_PATHS_ABS.get("ADITIM_LOGO_MAIN")
        pixmap = QPixmap(logo_path)
        scaled = pixmap.scaled(300, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.ui.label_logo.setPixmap(scaled)
        self.ui.label_logo.setText("")

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
        table = self.ui.tableWidget_dimension
        list_dimension = api_manager.directory.get('profiletool_dimension', [])
        table.setRowCount(len(list_dimension))
        table.setColumnCount(2)
        table.setHorizontalHeaderLabels(["Название", "Описание"])
        table.horizontalHeader().setStretchLastSection(True)

        for row, dimension in enumerate(list_dimension):
            item_name = QTableWidgetItem(dimension['name'])
            item_description = QTableWidgetItem(dimension.get('description', ''))

            item_name.setData(Qt.UserRole, dimension['id'])
            item_description.setData(Qt.UserRole, dimension['id'])

            table.setItem(row, 0, item_name)
            table.setItem(row, 1, item_description)

    def on_dimension_table_clicked(self):
        """Обработчик выбора размерности в таблице"""
        dimension_id = self.ui.tableWidget_dimension.currentItem().data(Qt.UserRole)
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
        """Обновление таблицы компонентов для выбранной размерности"""
        table = self.ui.tableWidget_component_type
        
        # Если размерность не выбрана, очищаем таблицу
        if not self.dimension:
            table.setRowCount(0)
            return
        
        # Фильтруем компоненты по выбранной размерности
        all_components = api_manager.directory.get('profiletool_component_type', [])
        list_component = [c for c in all_components if c.get('profiletool_dimension_id') == self.dimension['id']]
        
        table.setRowCount(len(list_component))
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["Название", "Ширина", "Высота", "Длина"])
        table.horizontalHeader().setStretchLastSection(True)

        for row, component_type in enumerate(list_component):
            item_name = QTableWidgetItem(component_type['name'])
            item_width = QTableWidgetItem(str(component_type.get('width', '')))
            item_height = QTableWidgetItem(str(component_type.get('height', '')))
            item_length = QTableWidgetItem(str(component_type.get('length', '')))

            item_name.setData(Qt.UserRole, component_type['id'])
            item_width.setData(Qt.UserRole, component_type['id'])
            item_height.setData(Qt.UserRole, component_type['id'])
            item_length.setData(Qt.UserRole, component_type['id'])

            table.setItem(row, 0, item_name)
            table.setItem(row, 1, item_width)
            table.setItem(row, 2, item_height)
            table.setItem(row, 3, item_length)

    def on_component_type_table_clicked(self):
        """Обработчик выбора компонента в таблице"""
        component_type_id = self.ui.tableWidget_component_type.currentItem().data(Qt.UserRole)
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
        table = self.ui.tableWidget_plan_stage
        
        # Если компонент не выбран, очищаем таблицу
        if not self.component_type:
            table.setRowCount(0)
            return
        
        # Фильтруем стадии по выбранному компоненту
        all_stages = api_manager.plan.get('task_component_stage', [])
        list_stage = [s for s in all_stages if s.get('profiletool_component_type_id') == self.component_type['id']]
        
        # Сортируем по номеру стадии
        list_stage.sort(key=lambda x: x.get('stage_num', 0))
        
        table.setRowCount(len(list_stage))
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["№", "Работа", "ID"])
        table.horizontalHeader().setStretchLastSection(True)

        for row, plan_stage in enumerate(list_stage):
            # Получаем работу
            work_name = ""
            if plan_stage.get('work_subtype_id'):
                work = api_manager.get_by_id('work_subtype', plan_stage['work_subtype_id'])
                if work:
                    work_name = work['name']

            item_stage_num = QTableWidgetItem(str(plan_stage.get('stage_num', '')))
            item_work = QTableWidgetItem(work_name)
            item_id = QTableWidgetItem(str(plan_stage['id']))

            item_stage_num.setData(Qt.UserRole, plan_stage['id'])
            item_work.setData(Qt.UserRole, plan_stage['id'])
            item_id.setData(Qt.UserRole, plan_stage['id'])

            table.setItem(row, 0, item_stage_num)
            table.setItem(row, 1, item_work)
            table.setItem(row, 2, item_id)

    def on_plan_stage_table_clicked(self):
        """Обработчик выбора стадии в таблице"""
        plan_stage_id = self.ui.tableWidget_plan_stage.currentItem().data(Qt.UserRole)
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
