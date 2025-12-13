"""Диалог для создания нового профиля."""
from PySide6.QtWidgets import QMessageBox
from PySide6.QtCore import QBuffer, Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QApplication
import base64
from ...base_dialog import BaseDialog
from ...api_manager import api_manager
from ...constant import UI_PATHS_ABS


class DialogCreateProfile(BaseDialog):
    """Диалог для создания нового профиля."""
    def __init__(self, parent):
        self.sketch_data = None
        super().__init__(UI_PATHS_ABS["DIALOG_CREATE_PROFILE"], api_manager, parent)

    def setup_ui(self):
        """Настраивает логику диалога."""
        # Подключаем обработчики кнопок
        self.ui.buttonBox.accepted.connect(self.accept)
        self.ui.buttonBox.rejected.connect(self.reject)
        # Подключаем обработчик кнопки вставки изображения
        self.ui.pushButton_paste_image.clicked.connect(self.paste_image)
        # Устанавливаем фокус на поле ввода артикула
        self.ui.lineEdit_article.setFocus()

    # =============================================================================
    # Валидация данных профиля
    # =============================================================================
    def validate_profile_data(self) -> bool:
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
        self.ui.label_image.setPixmap(scaled_pixmap)
        self.ui.label_image.setText("")
        # Сохраняем в base64
        self.sketch_data = self.pixmap_to_base64(scaled_pixmap)
  
    def pixmap_to_base64(self, pixmap: QPixmap):
        """Конвертирует QPixmap в строку формата data:image/png;base64."""
        buffer = QBuffer()
        buffer.open(QBuffer.WriteOnly)
        pixmap.save(buffer, "PNG", 85)
        image_data = buffer.data().data()

        base64_data = base64.b64encode(image_data).decode('utf-8')
        buffer.close()
        return f"data:image/png;base64,{base64_data}"

    # =============================================================================
    # Создание профиля
    # =============================================================================
    def create_profile(self):
        """Создаёт новый профиль после валидации данных."""
        if self.validate_profile_data():
            profile_data = {
                "article": self.ui.lineEdit_article.text().strip(),
                "description": self.ui.textEdit_description.toPlainText().strip(),
                "sketch": self.sketch_data
            }
            api_manager.api_profile.create_profile(profile_data)

        else:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, исправьте ошибки в форме.")

    def accept(self):
        """Принимает изменения и закрывает диалог"""
        self.create_profile()
        super().accept()