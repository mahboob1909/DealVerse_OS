"""
Database initialization script for DealVerse OS
"""
import logging
from sqlalchemy.orm import Session

from app.core.config import settings
from app.crud.crud_user import crud_user
from app.db.database import SessionLocal, init_db
from app.models.organization import Organization
from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import get_password_hash

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_initial_data(db: Session) -> None:
    """Create initial data for the application"""
    
    # Create default organization
    organization = db.query(Organization).filter(Organization.slug == "dealverse-demo").first()
    if not organization:
        organization = Organization(
            name="DealVerse Demo Organization",
            slug="dealverse-demo",
            description="Demo organization for DealVerse OS",
            subscription_tier="premium",
            subscription_status="active",
            contact_email="admin@dealverse.com",
            settings={
                "features": {
                    "ai_analysis": True,
                    "advanced_modeling": True,
                    "compliance_monitoring": True,
                    "real_time_collaboration": True
                },
                "limits": {
                    "max_users": 100,
                    "max_deals": 1000,
                    "storage_gb": 100
                }
            }
        )
        db.add(organization)
        db.commit()
        db.refresh(organization)
        logger.info(f"Created organization: {organization.name}")
    
    # Create superuser
    user = crud_user.get_by_email(db, email=settings.FIRST_SUPERUSER)
    if not user:
        user_in = UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            first_name="Admin",
            last_name="User",
            role="admin",
            organization_id=organization.id,
            is_active=True
        )
        user = crud_user.create(db, obj_in=user_in)
        user.is_superuser = True
        user.is_verified = True
        db.add(user)
        db.commit()
        logger.info(f"Created superuser: {user.email}")
    
    # Create sample users for different roles
    sample_users = [
        {
            "email": "manager@dealverse.com",
            "password": "manager123",
            "first_name": "Sarah",
            "last_name": "Johnson",
            "role": "manager",
            "title": "Managing Director",
            "department": "Investment Banking"
        },
        {
            "email": "analyst@dealverse.com", 
            "password": "analyst123",
            "first_name": "Michael",
            "last_name": "Chen",
            "role": "analyst",
            "title": "Investment Banking Analyst",
            "department": "Investment Banking"
        },
        {
            "email": "associate@dealverse.com",
            "password": "associate123", 
            "first_name": "Emily",
            "last_name": "Rodriguez",
            "role": "associate",
            "title": "Investment Banking Associate",
            "department": "Investment Banking"
        },
        {
            "email": "vp@dealverse.com",
            "password": "vp123",
            "first_name": "David",
            "last_name": "Thompson",
            "role": "vp",
            "title": "Vice President",
            "department": "Investment Banking"
        }
    ]
    
    for user_data in sample_users:
        existing_user = crud_user.get_by_email(db, email=user_data["email"])
        if not existing_user:
            user_in = UserCreate(
                email=user_data["email"],
                password=user_data["password"],
                first_name=user_data["first_name"],
                last_name=user_data["last_name"],
                role=user_data["role"],
                title=user_data.get("title"),
                department=user_data.get("department"),
                organization_id=organization.id,
                is_active=True
            )
            user = crud_user.create(db, obj_in=user_in)
            user.is_verified = True
            db.add(user)
            db.commit()
            logger.info(f"Created user: {user.email} ({user.role})")


def init_database() -> None:
    """Initialize the database with tables and initial data"""
    logger.info("Creating database tables...")
    
    # Create all tables
    init_db()
    
    # Create initial data
    db = SessionLocal()
    try:
        create_initial_data(db)
        logger.info("Database initialization completed successfully!")
    except Exception as e:
        logger.error(f"Error during database initialization: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    init_database()
