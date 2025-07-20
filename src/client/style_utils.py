"""
Utility functions for loading styles with constants
"""

import re
from .constants import COLORS, FONTS

def load_styles_with_constants(qss_file_path: str) -> str:
    """
    Load QSS file and replace color and font placeholders with actual values from constants.
    
    Args:
        qss_file_path: Path to the QSS file
        
    Returns:
        QSS string with replaced constants
    """
    try:
        with open(qss_file_path, "r", encoding="utf-8") as style_file:
            qss_content = style_file.read()
        
        # Заменяем цветовые константы
        for color_key, color_value in COLORS.items():
            # Поддерживаем два формата плейсхолдеров: {{COLOR_NAME}} и $COLOR_NAME
            placeholder_curly = f"{{{{{color_key}}}}}"
            placeholder_dollar = f"${color_key}"
            qss_content = qss_content.replace(placeholder_curly, color_value)
            qss_content = qss_content.replace(placeholder_dollar, color_value)
        
        # Заменяем шрифтовые константы
        for font_key, font_value in FONTS.items():
            placeholder_curly = f"{{{{{font_key}}}}}"
            placeholder_dollar = f"${font_key}"
            qss_content = qss_content.replace(placeholder_curly, font_value)
            qss_content = qss_content.replace(placeholder_dollar, font_value)
        
        return qss_content
    except Exception as e:
        print(f"Error loading styles from {qss_file_path}: {e}")
        return ""
