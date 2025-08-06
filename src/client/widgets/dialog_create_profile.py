"""
Диалог для создания нового профиля.
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


class DialogCreateProfile(QDialog):
    """Диалог для создания нового профиля."""
    profile_created = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.api_profile = ApiProfile()
        self.image_data = None  # Храним данные изображения в формате base64

        # Загружаем UI файл
        self.load_ui()

        # Настраиваем логику
        self.setup_logic()

    def load_ui(self):
        """Загружает UI из файла."""
        ui_file = QFile(UI_PATHS_ABS["DIALOG_CREATE_PROFILE"])
        ui_file.open(QFile.ReadOnly)

        loader = QUiLoader()
        self.ui = loader.load(ui_file, self)
        ui_file.close()

        # Заменяем layout
        self.setLayout(self.ui.layout())

    def setup_logic(self):
        """Настраивает логику диалога."""
        # Подключаем обработчики кнопок
        self.ui.buttonBox.accepted.connect(self.create_profile)
        self.ui.buttonBox.rejected.connect(self.reject)

        # Подключаем обработчик кнопки вставки изображения
        self.ui.pushButton_paste_image.clicked.connect(self.paste_image_from_clipboard)

        # Устанавливаем фокус на поле ввода артикула
        self.ui.lineEdit_article.setFocus()

    # =============================================================================
    # Работа с данными профиля
    # =============================================================================

    def validate_profile_data(self) -> bool:
        """Проверяет корректность введённых данных профиля.

        Валидация:
            - Артикул должен быть не пустым и содержать минимум 3 символа.

        Returns:
            bool: True, если данные валидны, иначе False.
        """
        article = self.ui.lineEdit_article.text().strip()
        if not article or len(article) < 3:
            return False
        return True

    def get_profile_data(self) -> Dict[str, Any]:
        """Собирает данные формы в словарь для отправки на сервер."""
        article = self.ui.lineEdit_article.text().strip()
        description = self.ui.textEdit_description.toPlainText().strip()
        return {
            "article": article,
            "description": description if description else None,
            "sketch": self.image_data if self.image_data else None
        }

    # =============================================================================
    # Обработка изображения
    # =============================================================================

    def paste_image_from_clipboard(self):
        """Вставляет изображение из буфера обмена."""
        try:
            clipboard = QApplication.clipboard()
            pixmap = clipboard.pixmap()

            if pixmap.isNull():
                QMessageBox.information(
                    self,
                    "Информация",
                    "В буфере обмена нет изображения"
                )
                return

            # Проверяем корректность изображения
            if pixmap.width() <= 0 or pixmap.height() <= 0:
                QMessageBox.warning(
                    self,
                    "Ошибка",
                    "Некорректное изображение в буфере обмена"
                )
                return

            # Масштабируем изображение
            scaled_pixmap = pixmap.scaled(
                100, 100,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )

            if scaled_pixmap.isNull() or scaled_pixmap.width() <= 0:
                QMessageBox.warning(
                    self,
                    "Ошибка",
                    "Не удалось обработать изображение"
                )
                return

            # Отображаем в интерфейсе
            self.ui.label_image.setPixmap(scaled_pixmap)
            self.ui.label_image.setText("")

            # Сохраняем в base64
            self.image_data = self.pixmap_to_base64(scaled_pixmap)

            QMessageBox.information(
                self,
                "Успех",
                "Изображение успешно вставлено!"
            )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Ошибка",
                f"Не удалось вставить изображение: {e}"
            )

    def pixmap_to_base64(self, pixmap: QPixmap) -> str:
        """Конвертирует QPixmap в строку формата data:image/png;base64."""
        try:
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

        except Exception as e:
            print(f"Ошибка конвертации pixmap в base64: {e}")
            return ""

    # =============================================================================
    # Создание профиля
    # =============================================================================

    def create_profile(self):
        """Создаёт новый профиль после валидации данных."""
        if not self.validate_profile_data():
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, исправьте ошибки в форме.")
            return

        profile_data = self.get_profile_data()
        result = self.api_profile.create_profile(profile_data)
        self.profile_created.emit(result)
        self.accept()