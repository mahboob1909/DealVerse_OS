#!/usr/bin/env python3
"""
Test Neon Database Connection for DealVerse OS
"""

import os
import sys
from pathlib import Path

def test_neon_connection():
    """Test Neon database connection and initialize if needed"""
    print("🔍 Testing Neon Database Connection")
    print("=" * 50)
    
    # Add backend to path
    backend_dir = Path("backend")
    sys.path.append(str(backend_dir / "app"))
    
    try:
        # Test settings loading
        print("📋 Loading configuration...")
        from app.core.config import settings
        print("✅ Configuration loaded successfully")
        
        # Check if Neon URL is configured
        if not settings.NEON_DATABASE_URL:
            print("❌ NEON_DATABASE_URL not found in .env file")
            return False
        
        print("✅ Neon URL configured")
        
        # Test database connection
        print("🔗 Testing database connection...")
        import psycopg2
        
        conn = psycopg2.connect(settings.NEON_DATABASE_URL)
        cursor = conn.cursor()
        
        # Test basic query
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"✅ Connected to: {version[:60]}...")
        
        # Test if tables exist
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tables = cursor.fetchall()
        
        if tables:
            print(f"✅ Found {len(tables)} existing tables")
            for table in tables[:5]:  # Show first 5 tables
                print(f"   - {table[0]}")
            if len(tables) > 5:
                print(f"   ... and {len(tables) - 5} more")
        else:
            print("⚠️  No tables found - database needs initialization")
        
        cursor.close()
        conn.close()
        
        print("🎉 Neon connection test successful!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("🔧 Make sure you're running from the correct directory")
        return False
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("🔧 Please check:")
        print("   1. Your Neon connection string is correct")
        print("   2. Your internet connection is working")
        print("   3. The Neon database is accessible")
        return False

def initialize_database():
    """Initialize database with tables and sample data"""
    print("\n🏗️  Initializing Database")
    print("=" * 30)
    
    backend_dir = Path("backend")
    if os.name == 'nt':  # Windows
        python_exe = backend_dir / "venv" / "Scripts" / "python.exe"
    else:  # Linux/Mac
        python_exe = backend_dir / "venv" / "bin" / "python"
    
    try:
        import subprocess
        
        # Run database initialization
        print("📊 Creating tables and sample data...")
        result = subprocess.run([
            str(python_exe), "-c",
            "import sys; sys.path.append('app'); from app.db.init_db import init_database; init_database()"
        ], cwd=backend_dir, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("✅ Database initialized successfully!")
            print("✅ Sample users and data created")
            return True
        else:
            print(f"❌ Database initialization failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Initialization error: {e}")
        return False

def main():
    """Main test function"""
    # Test connection first
    if not test_neon_connection():
        print("\n❌ Connection test failed")
        return False
    
    # Ask user if they want to initialize database
    print("\n" + "="*50)
    print("🎯 Database Connection Successful!")
    
    response = input("\n📊 Do you want to initialize the database with tables and sample data? (y/n): ").lower().strip()
    
    if response in ['y', 'yes']:
        if initialize_database():
            print("\n🎉 Setup Complete!")
            print("\n🚀 Next Steps:")
            print("1. Start backend: cd backend && venv\\Scripts\\python -m uvicorn app.main:app --reload")
            print("2. Start frontend: npm run dev")
            print("3. Open http://localhost:3000")
            print("4. Login with: admin@dealverse.com / changethis")
        else:
            print("\n❌ Database initialization failed")
            return False
    else:
        print("\n⚠️  Database not initialized")
        print("You can initialize it later by running this script again")
    
    return True

if __name__ == "__main__":
    main()
