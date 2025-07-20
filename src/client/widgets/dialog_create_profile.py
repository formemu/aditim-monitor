"""
Диалог для создания нового профиля
"""

from typing import Dict, Any, Optional
from PySide6.QtWidgets import QDialog, QMessageBox
from PySide6.QtCore import Signal, QFile, QBuffer, Qt
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QPixmap, QClipboard
from PySide6.QtWidgets import QApplication
import base64
import io
from ..style_utils import load_styles_with_constants
from ..api_client import ApiClient


class DialogCreateProfile(QDialog):
    """Диалог для создания нового профиля"""
    
    profile_created = Signal(dict)  # Сигнал об успешном создании профиля

    def __init__(self, api_client: ApiClient, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.image_data = None  # Храним данные изображения
        
        # Загружаем UI файл
        self.load_ui()
        
        # Применяем стили
        self.apply_styles()
        
        # Настраиваем логику
        self.setup_logic()

    def load_ui(self):
        """Загружает UI из файла"""
        ui_file_path = "src/client/ui/dialog_create_profile.ui"
        ui_file = QFile(ui_file_path)
        
        loader = QUiLoader()
        self.ui = loader.load(ui_file, self)
        ui_file.close()
        
        # Заменяем layout
        self.setLayout(self.ui.layout())

    def apply_styles(self):
        """Применяет стили к диалогу"""
        try:
            stylesheet = load_styles_with_constants("src/client/resources/styles/dialogs_template.qss")
            self.setStyleSheet(stylesheet)
        except Exception as e:
            print(f"Предупреждение: Не удалось загрузить стили: {e}")

    def setup_logic(self):
        """Настраивает логику диалога"""
        # Подключаем обработчики кнопок
        self.ui.buttonBox.accepted.connect(self.create_profile)
        self.ui.buttonBox.rejected.connect(self.reject)
        
        # Подключаем обработчик кнопки вставки изображения
        self.ui.pushButton_paste_image.clicked.connect(self.paste_image_from_clipboard)
        
        # Фокус на поле артикула
        self.ui.lineEdit_article.setFocus()

    def create_profile(self):
        """Создает новый профиль"""
        try:
            # Валидация данных
            profile_data = self.validate_and_get_data()
            
            # Отправляем запрос на сервер
            result = self.api_client.create_profile(profile_data)
            
            # Уведомляем об успехе
            QMessageBox.information(
                self, 
                "Успех", 
                f"Профиль '{profile_data['article']}' успешно создан!"
            )
            
            # Испускаем сигнал о создании профиля
            self.profile_created.emit(result)
            
            # Закрываем диалог
            self.accept()
            
        except ValueError as e:
            QMessageBox.warning(self, "Ошибка валидации", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось создать профиль: {e}")

    def validate_and_get_data(self) -> Dict[str, Any]:
        """Валидирует введенные данные и возвращает их"""
        article = self.ui.lineEdit_article.text().strip()
        
        # Проверка обязательных полей
        if not article:
            raise ValueError("Артикул профиля обязателен для заполнения")
        
        # Проверка длины артикула
        if len(article) < 3:
            raise ValueError("Артикул должен содержать минимум 3 символа")
        
        data = {
            "article": article,
            "sketch": self.image_data if self.image_data else None
        }
        
        return data

    def paste_image_from_clipboard(self):
        """Вставляет изображение из буфера обмена"""
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
            
            # Масштабируем изображение до 100x100
            scaled_pixmap = pixmap.scaled(100, 100, Qt.KeepAspectRatio)
            
            # Отображаем изображение в label
            self.ui.label_image.setPixmap(scaled_pixmap)
            self.ui.label_image.setText("")
            
            # Конвертируем в base64 для отправки на сервер
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
        """Конвертирует QPixmap в base64 строку"""
        # Сохраняем pixmap в байтовый буфер
        buffer = QBuffer()
        buffer.open(QBuffer.WriteOnly)
        pixmap.save(buffer, "PNG")
        
        # Конвертируем в base64
        image_data = buffer.data().data()
        base64_data = base64.b64encode(image_data).decode('utf-8')
        
        return f"data:image/png;base64,{base64_data}"

    def get_profile_data(self) -> Optional[Dict[str, Any]]:
        """Возвращает данные профиля без валидации (для предварительного просмотра)"""
        try:
            return self.validate_and_get_data()
        except ValueError:
            return None
