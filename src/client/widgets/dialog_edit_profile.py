"""
Диалог для редактирования существующего профиля.
"""

from typing import Dict, Any, Optional
from PySide6.QtWidgets import QDialog, QMessageBox
from PySide6.QtCore import Signal, QFile, QBuffer, Qt
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QPixmap, QClipboard
from PySide6.QtWidgets import QApplication
import base64
import io
from ..style_util import load_styles
from ..api.api_profile import ApiProfile
from ..constant import UI_PATHS_ABS


class DialogEditProfile(QDialog):
    """Диалог для редактирования существующего профиля."""
    profile_updated = Signal(dict)

    def __init__(self, profile_data: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.api_profile = ApiProfile()
        self.profile_data = profile_data
        self.sketch_data = profile_data.get('sketch')

        # Загружаем UI файл
        self.load_ui()

        # Настраиваем логику
        self.setup_logic()

        # Заполняем форму данными профиля
        self.setup_form()

    def load_ui(self):
        """Загружает UI из файла."""
        ui_file = QFile(UI_PATHS_ABS["DIALOG_EDIT_PROFILE"])
        ui_file.open(QFile.ReadOnly)

        loader = QUiLoader()
        self.ui = loader.load(ui_file, self)
        ui_file.close()

        # Заменяем layout
        self.setLayout(self.ui.layout())

    def setup_logic(self):
        """Настраивает логику диалога."""
        # Подключаем обработчики кнопок
        self.ui.buttonBox.accepted.connect(self.update_profile)
        self.ui.buttonBox.rejected.connect(self.reject)
        # Подключаем обработчик кнопки вставки изображения
        self.ui.pushButton_paste_image.clicked.connect(self.paste_image)

    def setup_form(self):
        """Заполняет форму данными редактируемого профиля."""
        # Заполняем текстовые поля
        article = self.profile_data.get('article')
        description = self.profile_data.get('description')
        
        self.ui.lineEdit_article.setText(article)
        self.ui.textEdit_description.setPlainText(description)

        # Загружаем изображение, если есть
        if self.sketch_data:
            self.load_sketch()

    def load_sketch(self):
        """Загружает и отображает эскиз профиля"""
        if not self.sketch_data:
            return
        base64_data = self.sketch_data.split(',')[1]
        image_data = base64.b64decode(base64_data)
        pixmap = QPixmap()
        if pixmap.loadFromData(image_data) and not pixmap.isNull():
            scaled = pixmap.scaled(200, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.ui.label_sketch.setPixmap(scaled)
            self.ui.label_sketch.setText("")
        else:
            self.ui.label_sketch.setText("Не удалось загрузить изображение")

    # =============================================================================
    # Работа с данными профиля
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
        self.ui.label_sketch.setPixmap(scaled_pixmap)
        self.ui.label_sketch.setText("")

        # Сохраняем в base64
        self.sketch_data = self.pixmap_to_base64(scaled_pixmap)

    def pixmap_to_base64(self, pixmap: QPixmap) -> str:
        """Конвертирует QPixmap в строку формата data:image/png;base64."""
        if pixmap.isNull() or pixmap.width() <= 0 or pixmap.height() <= 0:
            raise ValueError("Некорректный QPixmap")
        buffer = QBuffer()
        buffer.open(QBuffer.WriteOnly)
        success = pixmap.save(buffer, "PNG", 85)
        if not success:
            raise ValueError("Не удалось сохранить изображение в буфер")
        image_data = buffer.data().data()
        if not image_data:
            raise ValueError("Пустые данные изображения")
        base64_data = base64.b64encode(image_data).decode('utf-8')
        buffer.close()
        return f"data:image/png;base64,{base64_data}"

    # =============================================================================
    # Обновление профиля
    # =============================================================================

    def update_profile(self):
        """Обновляет существующий профиль после валидации данных."""
        if not self.validate_profile_data():
            return
        data = {
            "article": self.ui.lineEdit_article.text().strip(),
            "description": self.ui.textEdit_description.toPlainText().strip(),
            "sketch": self.sketch_data
        }

        # Отправляем запрос на обновление через API
        updated_profile = self.api_profile.update_profile(self.profile_data.get('id'), data)
        self.profile_updated.emit(updated_profile)
        self.accept()

