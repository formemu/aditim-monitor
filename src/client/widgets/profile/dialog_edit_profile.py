"""Диалог для редактирования существующего профиля."""
from PySide6.QtWidgets import QDialog
from PySide6.QtCore import QFile, QBuffer, Qt
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QApplication, QMessageBox
import base64
from ...constant import UI_PATHS_ABS
from ...api_manager import api_manager

class DialogEditProfile(QDialog):
    """Диалог для редактирования существующего профиля."""
    def __init__(self, profile_data, parent):
        super().__init__(parent)
        self.profile = profile_data
        self.sketch_data = profile_data.get('sketch')

        self.load_ui()
        self.setup_logic()
        self.setup_form()

    def load_ui(self):
        """Загружает UI из файла."""
        ui_file = QFile(UI_PATHS_ABS["DIALOG_EDIT_PROFILE"])
        ui_file.open(QFile.ReadOnly)
        loader = QUiLoader()
        self.ui = loader.load(ui_file, self)
        ui_file.close()
        self.setLayout(self.ui.layout())

    def setup_logic(self):
        """Настраивает логику диалога."""
        # Подключаем обработчики кнопок
        self.ui.buttonBox.accepted.connect(self.accept)
        self.ui.buttonBox.rejected.connect(self.reject)
        # Подключаем обработчик кнопки вставки изображения
        self.ui.pushButton_paste_image.clicked.connect(self.paste_image)

    def setup_form(self):
        """Заполняет форму данными редактируемого профиля."""
        # Заполняем текстовые поля
        article = self.profile.get('article')
        description = self.profile.get('description')
        
        self.ui.lineEdit_article.setText(article)
        self.ui.textEdit_description.setPlainText(description)

        # Загружаем изображение, если есть
        if self.sketch_data:
            self.load_sketch()

    def load_sketch(self):
        """Загружает и отображает эскиз профиля"""
        base64_data = self.sketch_data
        image_data = base64.b64decode(base64_data, validate=True)
        pixmap = QPixmap()
        if pixmap.loadFromData(image_data) and not pixmap.isNull():
            scaled = pixmap.scaled(200, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.ui.label_sketch.setPixmap(scaled)
            self.ui.label_sketch.setText("")
        else:
            self.ui.label_sketch.setText("Не удалось загрузить изображение")

    # =============================================================================
    # Валидация данных профиля
    # =============================================================================
    def validate_profile_data(self):
        """Проверяет корректность введённых данных профиля."""
        article = self.ui.lineEdit_article.text().strip()
        if not article or len(article) < 3:
            return False
        return True

    # =============================================================================
    # Обработка изображения
    # =============================================================================
    def paste_image(self):
        """Вставляет изображение из буфера обмена."""
        clipboard = QApplication.clipboard()
        pixmap = clipboard.pixmap()
        # Масштабируем изображение
        scaled_pixmap = pixmap.scaled(
            100, 100,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        # Отображаем в интерфейсе
        self.ui.label_sketch.setPixmap(scaled_pixmap)
        self.ui.label_sketch.setText("")
        # Сохраняем в base64
        self.sketch_data = self.pixmap_to_base64(scaled_pixmap)

    def pixmap_to_base64(self, pixmap):
        """Конвертирует QPixmap в строку формата data:image/png;base64."""
        buffer = QBuffer()
        buffer.open(QBuffer.WriteOnly)
        pixmap.save(buffer, "PNG", 85)
        image_data = buffer.data().data()

        base64_data = base64.b64encode(image_data).decode('utf-8')
        buffer.close()
        return f"data:image/png;base64,{base64_data}"
    # =============================================================================
    # Обновление профиля
    # =============================================================================
    def update_profile(self):
        """Обновляет существующий профиль."""
        if self.validate_profile_data():
            data_profile = {
                "article": self.ui.lineEdit_article.text().strip(),
                "description": self.ui.textEdit_description.toPlainText().strip(),
                "sketch": self.sketch_data
            }
            api_manager.api_profile.update_profile(self.profile.get('id'), data_profile)
        else:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, исправьте ошибки в форме.")
    
    def accept(self):
        """Принимает изменения и закрывает диалог"""
        self.update_profile()
        super().accept()
        