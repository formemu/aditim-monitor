import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from server.database import engine
from server.models import Base

DB_PATH = "queue.db"

def recreate_database():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"Deleted existing database file: {DB_PATH}")
    else:
        print(f"No existing database file found: {DB_PATH}")

    Base.metadata.create_all(bind=engine)
    print("Database and tables created successfully using SQLAlchemy ORM.")

if __name__ == "__main__":
    recreate_database()
