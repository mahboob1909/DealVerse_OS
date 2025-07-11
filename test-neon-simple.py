#!/usr/bin/env python3
"""
Simple Neon Database Connection Test
Tests connection directly without app dependencies
"""

import os
from pathlib import Path

def load_env_file():
    """Load environment variables from .env file"""
    env_file = Path("backend") / ".env"
    
    if not env_file.exists():
        print("❌ .env file not found in backend directory")
        return None
    
    env_vars = {}
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                env_vars[key] = value
    
    return env_vars

def test_neon_connection():
    """Test Neon database connection"""
    print("🔍 Simple Neon Database Connection Test")
    print("=" * 50)
    
    # Load environment variables
    print("📋 Loading environment variables...")
    env_vars = load_env_file()
    
    if not env_vars:
        return False
    
    # Get Neon URL
    neon_url = env_vars.get('NEON_DATABASE_URL')
    if not neon_url:
        print("❌ NEON_DATABASE_URL not found in .env file")
        print("Please make sure your .env file contains:")
        print("NEON_DATABASE_URL=postgresql://username:password@ep-xxx.neon.tech/dealverse_db?sslmode=require")
        return False
    
    print("✅ Neon URL found in .env file")
    print(f"🔗 Connecting to: {neon_url[:50]}...")
    
    try:
        # Test connection with psycopg2
        import psycopg2
        
        conn = psycopg2.connect(neon_url)
        cursor = conn.cursor()
        
        # Test basic query
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"✅ Connected successfully!")
        print(f"📊 PostgreSQL version: {version[:60]}...")
        
        # Check if any tables exist
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        table_count = cursor.fetchone()[0]
        
        if table_count > 0:
            print(f"✅ Found {table_count} existing tables")
            
            # List some tables
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                LIMIT 5
            """)
            tables = cursor.fetchall()
            for table in tables:
                print(f"   - {table[0]}")
        else:
            print("⚠️  No tables found - database is empty")
            print("📊 Database needs to be initialized")
        
        cursor.close()
        conn.close()
        
        print("\n🎉 Neon connection test PASSED!")
        return True
        
    except ImportError:
        print("❌ psycopg2 not installed")
        print("🔧 Install it with: backend\\venv\\Scripts\\pip install psycopg2-binary")
        return False
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Check your Neon connection string is correct")
        print("2. Make sure your internet connection is working")
        print("3. Verify the database exists in your Neon project")
        print("4. Check if your IP is allowed (Neon allows all by default)")
        return False

def create_basic_table():
    """Create a basic test table to verify write permissions"""
    print("\n🧪 Testing database write permissions...")
    
    env_vars = load_env_file()
    neon_url = env_vars.get('NEON_DATABASE_URL')
    
    try:
        import psycopg2
        
        conn = psycopg2.connect(neon_url)
        cursor = conn.cursor()
        
        # Create a simple test table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_connection (
                id SERIAL PRIMARY KEY,
                test_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Insert a test record
        cursor.execute("""
            INSERT INTO test_connection (test_message) 
            VALUES ('DealVerse OS connection test successful!')
        """)
        
        # Read it back
        cursor.execute("SELECT test_message FROM test_connection ORDER BY id DESC LIMIT 1")
        result = cursor.fetchone()
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"✅ Write test successful: {result[0]}")
        return True
        
    except Exception as e:
        print(f"❌ Write test failed: {e}")
        return False

def main():
    """Main test function"""
    # Test basic connection
    if not test_neon_connection():
        print("\n❌ Basic connection test failed")
        print("\n🔧 Next steps:")
        print("1. Double-check your Neon connection string")
        print("2. Make sure you copied it correctly to backend/.env")
        print("3. Verify your Neon database is running")
        return False
    
    # Test write permissions
    if create_basic_table():
        print("\n🎉 All tests passed! Your Neon database is ready.")
        print("\n🚀 Next steps:")
        print("1. Start backend: cd backend && venv\\Scripts\\python -m uvicorn app.main:app --reload")
        print("2. Start frontend: npm run dev")
        print("3. Open http://localhost:3000")
    else:
        print("\n⚠️  Connection works but write test failed")
        print("Check your database permissions")
    
    return True

if __name__ == "__main__":
    main()
