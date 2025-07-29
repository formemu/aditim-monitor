"""
Запускатор клиента для ADITIM Monitor
Запускает клиентское приложение из src/client
"""

import sys
from pathlib import Path

# Добавляем корень проекта в путь Python
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    # Импорт основного клиентского приложения
    from src.client.main import main
    
    if __name__ == "__main__":
        print("Запуск ADITIM Monitor...")
        sys.exit(main())
        
except ImportError as e:
    print(f"Ошибка импорта клиентского приложения: {e}")
    print("Убедитесь, что файлы клиента правильно установлены в src/client/")
    sys.exit(1)
except Exception as e:
    print(f"Ошибка запуска клиента: {e}")
    sys.exit(1)
