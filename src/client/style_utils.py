"""
Utility functions for loading styles with constants
"""

import re
from .constants import COLORS

def load_styles_with_constants(qss_file_path: str) -> str:
    """
    Load QSS file and replace color placeholders with actual values from constants.
    
    Args:
        qss_file_path: Path to the QSS file
        
    Returns:
        QSS string with replaced color constants
    """
    try:
        with open(qss_file_path, "r", encoding="utf-8") as style_file:
            qss_content = style_file.read()
        
        # Replace color placeholders with actual values
        for color_key, color_value in COLORS.items():
            placeholder = f"${color_key}"
            qss_content = qss_content.replace(placeholder, color_value)
        
        return qss_content
    except Exception as e:
        print(f"Error loading styles from {qss_file_path}: {e}")
        return ""
