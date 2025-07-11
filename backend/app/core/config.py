"""
Configuration settings for DealVerse OS Backend
"""
import secrets
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, EmailStr, HttpUrl, field_validator, ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""

    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="allow"  # Allow extra fields from .env
    )
    
    # API Configuration
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    PROJECT_NAME: str = "DealVerse OS"
    VERSION: str = "0.1.0"
    
    # CORS Configuration
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://localhost:3003",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:3002",
        "http://127.0.0.1:3003",
        "http://127.0.0.1:8000",
    ]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # Database Configuration
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_DB: str = "dealverse_db"
    POSTGRES_PORT: str = "5432"
    DATABASE_URL: Optional[str] = None
    NEON_DATABASE_URL: Optional[str] = None

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str], info) -> Any:
        if isinstance(v, str):
            return v
        # For now, use a simple string format since PostgresDsn.build is complex in v2
        values = info.data if hasattr(info, 'data') else {}
        user = values.get("POSTGRES_USER", "postgres")
        password = values.get("POSTGRES_PASSWORD", "")
        host = values.get("POSTGRES_SERVER", "localhost")
        port = values.get("POSTGRES_PORT", "5432")
        db = values.get("POSTGRES_DB", "dealverse_db")
        return f"postgresql://{user}:{password}@{host}:{port}/{db}"

    # Redis Configuration
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Celery Configuration
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    
    # File Storage (AWS S3)
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "us-east-1"
    S3_BUCKET_NAME: Optional[str] = None

    # S3 Advanced Configuration
    AWS_KMS_KEY_ID: Optional[str] = None  # For enhanced encryption of confidential documents
    S3_BACKUP_BUCKET_NAME: Optional[str] = None  # Cross-region backup bucket
    AWS_BACKUP_REGION: str = "us-west-2"  # Backup region for disaster recovery
    BACKUP_RETENTION_DAYS: int = 90  # Backup retention period

    # CloudFront CDN Configuration
    CLOUDFRONT_DOMAIN: Optional[str] = None  # CloudFront distribution domain
    CLOUDFRONT_DISTRIBUTION_ID: Optional[str] = None  # Distribution ID for cache management
    CLOUDFRONT_PRIVATE_KEY_PATH: Optional[str] = None  # Path to private key for signed URLs
    CLOUDFRONT_KEY_PAIR_ID: Optional[str] = None  # Key pair ID for signed URLs

    # File Upload Configuration
    MAX_FILE_SIZE_MB: int = 50  # Maximum file size in MB
    ALLOWED_FILE_TYPES: List[str] = [
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "application/vnd.ms-powerpoint",
        "text/plain",
        "text/csv",
        "image/jpeg",
        "image/png",
        "image/tiff"
    ]
    
    # External API Keys
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    
    # Email Configuration
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: Optional[int] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[EmailStr] = None
    EMAILS_FROM_NAME: Optional[str] = None
    
    # Monitoring and Logging
    SENTRY_DSN: Optional[str] = None
    LOG_LEVEL: str = "INFO"
    
    # Security Configuration
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1", "0.0.0.0"]
    RATE_LIMIT_PER_MINUTE: int = 60

    # Enhanced Security Settings
    MAX_LOGIN_ATTEMPTS: int = 5
    ACCOUNT_LOCKOUT_DURATION_MINUTES: int = 15
    PASSWORD_MIN_LENGTH: int = 8
    PASSWORD_REQUIRE_UPPERCASE: bool = True
    PASSWORD_REQUIRE_LOWERCASE: bool = True
    PASSWORD_REQUIRE_NUMBERS: bool = True
    PASSWORD_REQUIRE_SPECIAL_CHARS: bool = True
    PASSWORD_HISTORY_COUNT: int = 5  # Remember last 5 passwords

    # Session Security
    SESSION_TIMEOUT_MINUTES: int = 480  # 8 hours
    CONCURRENT_SESSIONS_LIMIT: int = 5  # Max concurrent sessions per user

    # Token Security
    TOKEN_BLACKLIST_ENABLED: bool = True
    TOKEN_ROTATION_ENABLED: bool = True

    # Security Headers
    SECURITY_HEADERS_ENABLED: bool = True
    CONTENT_SECURITY_POLICY: str = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' https:; connect-src 'self' https:; frame-ancestors 'none';"

    # Audit Logging
    AUDIT_LOG_ENABLED: bool = True
    AUDIT_LOG_RETENTION_DAYS: int = 90
    
    # Superuser Configuration
    FIRST_SUPERUSER: EmailStr = "admin@dealverse.com"
    FIRST_SUPERUSER_PASSWORD: str = "changethis"
    
    # Testing
    TESTING: bool = False

    # AI Configuration (OpenRouter)
    OPENROUTER_API_KEY: Optional[str] = None
    OPENROUTER_MODEL: str = "deepseek/deepseek-chat"
    OPENROUTER_MAX_TOKENS: int = 4000
    OPENROUTER_TEMPERATURE: float = 0.1
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    OPENROUTER_SITE_URL: Optional[str] = None
    OPENROUTER_SITE_NAME: Optional[str] = None
    AI_PROVIDER: str = "openrouter"
    AI_ENABLE_FALLBACK: bool = True
    AI_REQUEST_TIMEOUT: int = 60
    AI_MAX_RETRIES: int = 3

    # FastSpring Configuration
    FASTSPRING_API_USERNAME: Optional[str] = None
    FASTSPRING_API_PASSWORD: Optional[str] = None
    FASTSPRING_STORE_ID: Optional[str] = None
    FASTSPRING_WEBHOOK_SECRET: Optional[str] = None
    FASTSPRING_TEST_MODE: bool = True


settings = Settings()
