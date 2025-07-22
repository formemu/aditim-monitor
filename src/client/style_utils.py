
"""
Утилиты для загрузки QSS-стилей с подстановкой констант
"""


# Импортируем словари цветов и шрифтов из constants.py
from .constants import COLORS, FONTS

def load_styles_with_constants(qss_file_path: str) -> str:
    """
    Загружает QSS-файл и подставляет значения цветовых и шрифтовых констант.
    
    Аргументы:
        qss_file_path: путь к QSS-файлу
    
    Возвращает:
        Строку QSS с подставленными константами
    """
    try:
        # Открываем QSS-файл для чтения
        with open(qss_file_path, "r", encoding="utf-8") as style_file:
            qss_content = style_file.read()
        
        # --- Замена цветовых констант ---
        # Проходим по всем ключам и значениям из COLORS
        for color_key, color_value in COLORS.items():
            # Поддерживаются два формата плейсхолдеров: {{COLOR_NAME}} и $COLOR_NAME
            placeholder_curly = f"{{{{{color_key}}}}}"
            placeholder_dollar = f"${color_key}"
            # Заменяем оба варианта на реальное значение цвета
            qss_content = qss_content.replace(placeholder_curly, color_value)
            qss_content = qss_content.replace(placeholder_dollar, color_value)
        
        # --- Замена шрифтовых констант ---
        # Аналогично заменяем плейсхолдеры для шрифтов
        for font_key, font_value in FONTS.items():
            placeholder_curly = f"{{{{{font_key}}}}}"
            placeholder_dollar = f"${font_key}"
            qss_content = qss_content.replace(placeholder_curly, font_value)
            qss_content = qss_content.replace(placeholder_dollar, font_value)
        
        # Возвращаем итоговую строку QSS
        return qss_content
    except Exception as e:
        # В случае ошибки выводим сообщение и возвращаем пустую строку
        print(f"Ошибка при загрузке стилей из {qss_file_path}: {e}")
        return ""
