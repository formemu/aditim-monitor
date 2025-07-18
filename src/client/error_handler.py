"""
Error handling utilities for the ADITIM Monitor Client.
"""

from PySide6.QtWidgets import QMessageBox

def show_error_message(parent, title, message):
    """
    Displays a standardized error message box.
    """
    QMessageBox.warning(parent, title, message)

def handle_api_error(parent, error):
    """
    Handles API errors by showing a specific message.
    """
    message = f"Не удалось подключиться к серверу:\n{error}\n\nПроверьте, что сервер запущен."
    show_error_message(parent, "Ошибка подключения", message)
