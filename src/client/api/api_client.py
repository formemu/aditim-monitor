"""Базовый API клиент для взаимодействия с сервером"""

import httpx
from typing import Dict, Any
from ..constant import API_BASE_URL, API_TIMEOUT


class ApiClient:
    """Базовый API клиент"""
    
    def __init__(self, base_url: str = API_BASE_URL):
        """Инициализация клиента API"""
        self.base_url = base_url.rstrip('/')
        self.timeout = API_TIMEOUT
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[Any, Any] | None:
        """Выполнение HTTP-запроса к серверу"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        with httpx.Client(timeout=self.timeout) as client:
            response = client.request(method, url, **kwargs)
            response.raise_for_status()

            # Если статус 204 No Content или 205 Reset Content — нет тела
            if response.status_code in (204, 205):
                return None

            # Если есть тело — возвращаем JSON
            if response.text:
                return response.json()

            # На всякий случай
            return None