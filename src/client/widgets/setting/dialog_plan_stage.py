"""Диалог создания/редактирования стадии изготовления"""
from PySide6.QtWidgets import QDialog, QMessageBox
from PySide6.QtCore import QFile
from PySide6.QtUiTools import QUiLoader
from ...constant import UI_PATHS_ABS, get_style_path
from ...style_util import load_styles
from ...api_manager import api_manager

class DialogPlanStage(QDialog):
    """Диалог для создания или редактирования стадии изготовления"""
    def __init__(self, parent=None, plan_stage=None, component_type=None):
        super().__init__(parent)
        self.plan_stage = plan_stage
        self.component_type = component_type
        self.is_edit_mode = plan_stage is not None
        self.load_ui()
        self.setup_ui()
        self.load_work_list()
        if self.is_edit_mode:
            self.load_plan_stage_data()

    def load_ui(self):
        """Загрузка UI из файла"""
        ui_file = QFile(UI_PATHS_ABS["DIALOG_PLAN_STAGE"])
        ui_file.open(QFile.ReadOnly)
        loader = QUiLoader()
        self.ui = loader.load(ui_file, self)
        ui_file.close()
        
        # Копируем геометрию и заголовок
        self.setWindowTitle(self.ui.windowTitle())
        self.setGeometry(self.ui.geometry())
        self.setLayout(self.ui.layout())

    def setup_ui(self):
        """Настройка UI компонентов"""
        self.setStyleSheet(load_styles(get_style_path("DIALOGS")))
        
        # Меняем заголовок в зависимости от режима
        if self.is_edit_mode:
            self.setWindowTitle("Редактирование стадии")
        else:
            self.setWindowTitle("Создание стадии")
        
        # Показываем название компонента
        if self.component_type:
            self.ui.label_component_type_name.setText(self.component_type['name'])
        
        # Подключаем валидацию
        self.ui.buttonBox.accepted.connect(self.validate_and_accept)
        self.ui.buttonBox.rejected.connect(self.reject)

    def load_work_list(self):
        """Загрузка списка работ"""
        self.ui.comboBox_work.clear()
        list_work = api_manager.directory.get('work_subtype', [])
        
        for work in list_work:
            self.ui.comboBox_work.addItem(work['name'], work['id'])

    def load_plan_stage_data(self):
        """Загрузка данных стадии для редактирования"""
        if self.plan_stage:
            # Выбираем работу
            work_id = self.plan_stage.get('work_subtype_id')
            if work_id:
                index = self.ui.comboBox_work.findData(work_id)
                if index >= 0:
                    self.ui.comboBox_work.setCurrentIndex(index)
            
            # Устанавливаем номер этапа
            self.ui.spinBox_stage_num.setValue(self.plan_stage.get('stage_num', 1))

    def validate_and_accept(self):
        """Валидация данных перед принятием"""
        if self.ui.comboBox_work.currentIndex() < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите работу")
            return
        
        self.accept()

    def get_plan_stage_data(self):
        """Получение данных из формы"""
        return {
            "profiletool_component_type_id": self.component_type['id'],
            "work_subtype_id": self.ui.comboBox_work.currentData(),
            "stage_num": self.ui.spinBox_stage_num.value()
        }
