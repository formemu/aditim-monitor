#!/usr/bin/env python3
"""
Database checker utility for ADITIM Monitor
Проверяет состояние базы данных и отображает статистику
"""

import sys
import os
from pathlib import Path
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from src.server.database import engine, Base
    from src.server.models.task import Task
    from src.server.models.product import ModelProduct, Profile
    from src.server.models.directory import DirDepartment, DirTaskStatus
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure you're running from the project root directory")
    sys.exit(1)


def check_database_connection():
    """Check if database connection is working"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False


def get_table_stats(session):
    """Get statistics for each table"""
    stats = {}
    
    # Tasks statistics
    try:
        stats['tasks'] = {
            'total': session.query(Task).count(),
            'by_status': {}
        }
        
        # Tasks by status
        statuses = session.query(DirTaskStatus).all()
        for status in statuses:
            count = session.query(Task).filter(Task.status_id == status.id).count()
            stats['tasks']['by_status'][status.name] = count
            
    except Exception as e:
        stats['tasks'] = {'error': str(e)}
    
    # Products statistics
    try:
        stats['products'] = session.query(ModelProduct).count()
    except Exception as e:
        stats['products'] = {'error': str(e)}
    
    # Profiles statistics
    try:
        stats['profiles'] = session.query(Profile).count()
    except Exception as e:
        stats['profiles'] = {'error': str(e)}
    
    # Directories statistics
    try:
        stats['directories'] = {
            'departments': session.query(DirDepartment).count(),
            'statuses': session.query(DirTaskStatus).count()
        }
    except Exception as e:
        stats['directories'] = {'error': str(e)}
    
    return stats


def check_tables_exist():
    """Check if all required tables exist"""
    required_tables = [
        'task', 'product', 'profile', 'product_component', 'profile_component',
        'dir_departament', 'dir_queue_status', 'dir_type_work', 'dir_component'
    ]
    
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    
    missing_tables = [table for table in required_tables if table not in existing_tables]
    
    return existing_tables, missing_tables


def main():
    """Main function"""
    print("=" * 50)
    print("ADITIM Monitor Database Checker")
    print("=" * 50)
    
    # Check database connection
    print("\n1. Checking database connection...")
    if not check_database_connection():
        print("❌ Database connection failed!")
        return False
    print("✅ Database connection successful!")
    
    # Check tables
    print("\n2. Checking database tables...")
    existing_tables, missing_tables = check_tables_exist()
    
    print(f"📊 Found {len(existing_tables)} tables:")
    for table in sorted(existing_tables):
        print(f"   - {table}")
    
    if missing_tables:
        print(f"\n⚠️  Missing {len(missing_tables)} tables:")
        for table in missing_tables:
            print(f"   - {table}")
        print("\n💡 Run 'python init_db.py' to create missing tables")
    else:
        print("\n✅ All required tables exist!")
    
    # Get statistics
    print("\n3. Database statistics...")
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        stats = get_table_stats(session)
        
        # Tasks statistics
        if 'error' in stats.get('tasks', {}):
            print(f"❌ Tasks table error: {stats['tasks']['error']}")
        else:
            print(f"📋 Tasks: {stats['tasks']['total']} total")
            if stats['tasks']['by_status']:
                print("   By status:")
                for status, count in stats['tasks']['by_status'].items():
                    print(f"     - {status}: {count}")
        
        # Products and Profiles
        if isinstance(stats.get('products'), int):
            print(f"📦 Products: {stats['products']}")
        else:
            print(f"❌ Products error: {stats.get('products', {}).get('error', 'Unknown')}")
            
        if isinstance(stats.get('profiles'), int):
            print(f"🔧 Profiles: {stats['profiles']}")
        else:
            print(f"❌ Profiles error: {stats.get('profiles', {}).get('error', 'Unknown')}")
        
        # Directories
        if 'error' in stats.get('directories', {}):
            print(f"❌ Directories error: {stats['directories']['error']}")
        else:
            dirs = stats['directories']
            print(f"📁 Directories:")
            print(f"   - Departments: {dirs['departments']}")
            print(f"   - Statuses: {dirs['statuses']}")
        
    except Exception as e:
        print(f"❌ Error getting statistics: {e}")
    finally:
        session.close()
    
    print("\n" + "=" * 50)
    print("Database check completed!")
    print("=" * 50)
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
