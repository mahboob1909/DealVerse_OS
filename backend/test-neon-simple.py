#!/usr/bin/env python3
"""
Simple Neon Database Connection Test
Tests connection without complex dependencies
"""

import os
import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.append(str(Path(__file__).parent / "app"))

try:
    from app.core.config import settings
    print("✅ Settings loaded successfully")
    print(f"🔗 Database URL configured: {bool(settings.NEON_DATABASE_URL)}")
except Exception as e:
    print(f"❌ Error loading settings: {e}")
    sys.exit(1)

# Test with psycopg2 (synchronous) instead of asyncpg
try:
    import psycopg2
    from urllib.parse import urlparse
    
    # Get database URL
    db_url = settings.NEON_DATABASE_URL or str(settings.DATABASE_URL)
    
    if not db_url:
        print("❌ No database URL found in settings")
        sys.exit(1)
    
    print(f"🔍 Testing connection to Neon database...")
    
    # Connect to database
    conn = psycopg2.connect(db_url)
    cursor = conn.cursor()
    
    # Test query
    cursor.execute("SELECT version();")
    version = cursor.fetchone()[0]
    
    print(f"✅ Connected successfully!")
    print(f"📊 PostgreSQL version: {version}")
    
    # Close connection
    cursor.close()
    conn.close()
    
    print("🎉 Neon database connection test passed!")
    print("🚀 You can now proceed with the full setup")
    
except ImportError as e:
    print(f"❌ Missing required package: {e}")
    print("🔧 Please install missing dependencies:")
    print("   pip install psycopg2-binary")
    
except Exception as e:
    print(f"❌ Database connection failed: {e}")
    print("🔧 Please check:")
    print("   1. Your Neon connection string is correct")
    print("   2. Your internet connection is working")
    print("   3. The database exists in Neon")
