"""Диалог для создания инструмента профиля"""
from ...base_dialog import BaseDialog
from ...constant import UI_PATHS_ABS
from ...api_manager import api_manager


class DialogCreateProfiletoolComponent(BaseDialog):
    """Диалог для создания инструмента профиля с компонентами"""
    def __init__(self, parent=None, profiletool=None):
        self.profiletool = profiletool
        super().__init__(UI_PATHS_ABS["DIALOG_CREATE_PROFILETOOL_COMPONENT"], api_manager, parent)
        
        # Устанавливаем заголовок
        self.setWindowTitle("Создание компонента инструмента профиля")
        self.setModal(True)
        
    def setup_ui(self):
        """Настраивает UI компонентов после загрузки"""
        self.load_component_type()
        # Подключаем обработчики кнопок
        self.ui.buttonBox.accepted.connect(self.accept)
        self.ui.buttonBox.rejected.connect(self.reject)

    def load_component_type(self):
        list_filtered_type = [
            type for type in self.api_manager.directory['component_type']
            if type['profiletool_dimension_id'] == self.profiletool['dimension']['id']
        ]       
        self.ui.comboBox_component_type.clear()
        for component_type in list_filtered_type:
            self.ui.comboBox_component_type.addItem(component_type['name'], component_type['id'])


    def create_profiletool_component(self):
        """Создает новый инструмент профиля"""
        type_id = self.ui.comboBox_component_type.currentData()
        description = self.ui.textEdit_description.toPlainText().strip()
        component = {
            "type_id": type_id,
            "description": description,
            "variant": self.ui.lineEdit_component_variant.text().strip()
        }
        api_manager.api_profiletool.create_profiletool_component(self.profiletool['id'], component)

    def accept(self):
        """Принимает изменения и закрывает диалог"""
        self.create_profiletool_component()
        super().accept()
