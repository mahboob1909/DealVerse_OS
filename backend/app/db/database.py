"""
Database configuration and session management
"""
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool, QueuePool
from sqlalchemy.engine import Engine
import logging
import time

from app.core.config import settings

logger = logging.getLogger(__name__)

# Determine which database URL to use
database_url = settings.NEON_DATABASE_URL or str(settings.DATABASE_URL)

# Connection pool configuration
def get_pool_config():
    """Get optimized connection pool configuration based on environment"""
    if settings.ENVIRONMENT == "production":
        return {
            "pool_size": 20,           # Base number of connections
            "max_overflow": 30,        # Additional connections when needed
            "pool_timeout": 30,        # Timeout to get connection from pool
            "pool_recycle": 3600,      # Recycle connections every hour
            "pool_pre_ping": True,     # Validate connections before use
        }
    elif settings.ENVIRONMENT == "development":
        return {
            "pool_size": 5,
            "max_overflow": 10,
            "pool_timeout": 30,
            "pool_recycle": 1800,      # 30 minutes for development
            "pool_pre_ping": True,
        }
    else:  # testing or other
        return {
            "pool_size": 2,
            "max_overflow": 5,
            "pool_timeout": 10,
            "pool_recycle": 300,       # 5 minutes for testing
            "pool_pre_ping": True,
        }

# Create SQLAlchemy engine
if settings.TESTING:
    # Use SQLite for testing
    engine = create_engine(
        "sqlite:///./test.db",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False  # Disable SQL logging in tests
    )
else:
    # Use PostgreSQL for development/production with optimized pooling
    pool_config = get_pool_config()

    engine = create_engine(
        database_url,
        poolclass=QueuePool,
        echo=settings.DEBUG and settings.ENVIRONMENT == "development",  # SQL logging only in dev
        **pool_config
    )

# Add connection event listeners for monitoring and health checks
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Set SQLite pragmas for better performance (only for SQLite)"""
    if "sqlite" in str(engine.url):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA cache_size=1000")
        cursor.execute("PRAGMA temp_store=MEMORY")
        cursor.close()

@event.listens_for(engine, "checkout")
def receive_checkout(dbapi_connection, connection_record, connection_proxy):
    """Log connection checkout for monitoring"""
    connection_record.info['checkout_time'] = time.time()
    logger.debug(f"Connection checked out: {id(dbapi_connection)}")

@event.listens_for(engine, "checkin")
def receive_checkin(dbapi_connection, connection_record):
    """Log connection checkin and calculate usage time"""
    if 'checkout_time' in connection_record.info:
        checkout_time = connection_record.info['checkout_time']
        usage_time = time.time() - checkout_time
        logger.debug(f"Connection checked in: {id(dbapi_connection)}, usage time: {usage_time:.2f}s")

        # Log long-running connections
        if usage_time > 30:  # More than 30 seconds
            logger.warning(f"Long-running database connection detected: {usage_time:.2f}s")

@event.listens_for(engine, "invalidate")
def receive_invalidate(dbapi_connection, connection_record, exception):
    """Log connection invalidation"""
    logger.warning(f"Connection invalidated: {id(dbapi_connection)}, exception: {exception}")

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()


def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_connection_pool_status():
    """Get current connection pool status"""
    pool = engine.pool
    return {
        "pool_size": pool.size(),
        "checked_in_connections": pool.checkedin(),
        "checked_out_connections": pool.checkedout(),
        "overflow_connections": pool.overflow(),
        "invalid_connections": pool.invalid(),
        "total_connections": pool.size() + pool.overflow(),
        "pool_timeout": getattr(pool, '_timeout', None),
        "max_overflow": getattr(pool, '_max_overflow', None),
    }

def check_database_health():
    """Check database connection health"""
    try:
        # Test basic connection
        with engine.connect() as connection:
            result = connection.execute("SELECT 1")
            result.fetchone()

        # Get pool status
        pool_status = get_connection_pool_status()

        # Check for potential issues
        warnings = []
        if pool_status["checked_out_connections"] > pool_status["pool_size"] * 0.8:
            warnings.append("High connection usage detected")

        if pool_status["invalid_connections"] > 0:
            warnings.append(f"{pool_status['invalid_connections']} invalid connections found")

        return {
            "status": "healthy",
            "pool_status": pool_status,
            "warnings": warnings,
            "timestamp": time.time()
        }

    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": time.time()
        }

def optimize_connection_for_query(db_session, query_type: str = "read"):
    """Optimize database connection settings for specific query types"""
    try:
        if query_type == "read":
            # Optimize for read queries
            db_session.execute("SET statement_timeout = '30s'")
            db_session.execute("SET lock_timeout = '10s'")
        elif query_type == "write":
            # Optimize for write queries
            db_session.execute("SET statement_timeout = '60s'")
            db_session.execute("SET lock_timeout = '30s'")
        elif query_type == "analytics":
            # Optimize for long-running analytics queries
            db_session.execute("SET statement_timeout = '300s'")
            db_session.execute("SET work_mem = '256MB'")
    except Exception as e:
        logger.warning(f"Failed to optimize connection for {query_type}: {e}")


# Database initialization
def init_db():
    """Initialize database tables"""
    # Import all models here to ensure they are registered with SQLAlchemy
    from app.models import user, organization, deal, client, task, document, financial_model, presentation

    # Set up presentation relationships
    from app.models.presentation import add_presentation_relationships
    add_presentation_relationships()

    # Create all tables
    Base.metadata.create_all(bind=engine)
