"""Запускает серверное приложение из src/server"""

import sys
import uvicorn
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    # Import the main server application
    from src.server.main import app
    
    if __name__ == "__main__":
        print("Starting ADITIM Monitor Server...")
        uvicorn.run(
            "src.server.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="debug"
        )
        
except ImportError as e:
    print(f"Error importing server application: {e}")
    print("Make sure the server files are properly installed in src/server/")
    sys.exit(1)
except Exception as e:
    print(f"Error starting server: {e}")
    sys.exit(1)
