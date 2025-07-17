"""
Client launcher for ADITIM Monitor
Запускает клиентское приложение из src/client
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    # Import the main client application
    from src.client.main import main
    
    if __name__ == "__main__":
        print("Starting ADITIM Monitor Client...")
        sys.exit(main())
        
except ImportError as e:
    print(f"Error importing client application: {e}")
    print("Make sure the client files are properly installed in src/client/")
    sys.exit(1)
except Exception as e:
    print(f"Error starting client: {e}")
    sys.exit(1)
