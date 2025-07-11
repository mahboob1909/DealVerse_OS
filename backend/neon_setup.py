"""
Neon Database Setup Script for DealVerse OS
"""
import os
import sys
import asyncio
import asyncpg
from urllib.parse import urlparse
from pathlib import Path

# Add the app directory to Python path
sys.path.append(str(Path(__file__).parent / "app"))

from app.core.config import settings


async def test_neon_connection(database_url: str) -> bool:
    """Test connection to Neon database"""
    try:
        # Parse the database URL
        parsed = urlparse(database_url)
        
        # Connect to the database
        conn = await asyncpg.connect(
            host=parsed.hostname,
            port=parsed.port or 5432,
            user=parsed.username,
            password=parsed.password,
            database=parsed.path[1:] if parsed.path else None,
            ssl='require'  # Neon requires SSL
        )
        
        # Test the connection
        result = await conn.fetchval('SELECT version()')
        print(f"✅ Connected to Neon PostgreSQL: {result}")
        
        # Close the connection
        await conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Failed to connect to Neon database: {e}")
        return False


async def setup_neon_database():
    """Set up Neon database for DealVerse OS"""
    print("🚀 Setting up Neon Database for DealVerse OS...")
    
    # Check if Neon database URL is configured
    neon_url = settings.NEON_DATABASE_URL or os.getenv("NEON_DATABASE_URL")
    
    if not neon_url:
        print("❌ NEON_DATABASE_URL not found in environment variables")
        print("\n📋 To set up Neon database:")
        print("1. Go to https://neon.com and create an account")
        print("2. Create a new project")
        print("3. Copy the connection string")
        print("4. Add it to your .env file as NEON_DATABASE_URL")
        print("\nExample:")
        print("NEON_DATABASE_URL=postgresql://username:password@ep-xxx.us-east-1.aws.neon.tech/dealverse_db")
        return False
    
    print(f"🔗 Testing connection to Neon database...")
    
    # Test the connection
    if not await test_neon_connection(neon_url):
        return False
    
    print("✅ Neon database connection successful!")
    
    # Initialize the database schema
    print("\n📊 Initializing database schema...")
    try:
        from app.db.init_db import init_database
        init_database()
        print("✅ Database schema initialized successfully!")
    except Exception as e:
        print(f"❌ Failed to initialize database schema: {e}")
        return False
    
    print("\n🎉 Neon database setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Start the backend server: uvicorn app.main:app --reload")
    print("2. Access API docs: http://localhost:8000/api/v1/docs")
    print("3. Test authentication with the sample users:")
    print("   - admin@dealverse.com / changethis (admin)")
    print("   - manager@dealverse.com / manager123 (manager)")
    print("   - analyst@dealverse.com / analyst123 (analyst)")
    
    return True


def create_env_template():
    """Create .env file with Neon configuration template"""
    env_content = """# DealVerse OS Environment Configuration

# Neon Database Configuration
NEON_DATABASE_URL=postgresql://username:password@ep-xxx.us-east-1.aws.neon.tech/dealverse_db
DATABASE_URL=${NEON_DATABASE_URL}

# JWT Configuration
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Environment
ENVIRONMENT=development
DEBUG=True
API_V1_STR=/api/v1

# CORS Configuration (Frontend URLs)
BACKEND_CORS_ORIGINS=["http://localhost:3000", "http://localhost:3001"]

# Superuser Configuration
FIRST_SUPERUSER=admin@dealverse.com
FIRST_SUPERUSER_PASSWORD=changethis

# External API Keys (Optional)
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key

# File Storage (AWS S3) - Optional
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_REGION=us-east-1
S3_BUCKET_NAME=dealverse-documents

# Redis Configuration (Optional)
REDIS_URL=redis://localhost:6379/0

# Monitoring (Optional)
SENTRY_DSN=your-sentry-dsn
LOG_LEVEL=INFO
"""
    
    env_path = Path(".env")
    if not env_path.exists():
        with open(env_path, "w") as f:
            f.write(env_content)
        print("✅ Created .env file template")
        print("⚠️  Please update the NEON_DATABASE_URL with your actual connection string")
        return True
    else:
        print("✅ .env file already exists")
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Setup Neon Database for DealVerse OS")
    parser.add_argument(
        "--create-env",
        action="store_true",
        help="Create .env file template"
    )
    
    args = parser.parse_args()
    
    if args.create_env:
        create_env_template()
    else:
        # Run the async setup
        asyncio.run(setup_neon_database())
