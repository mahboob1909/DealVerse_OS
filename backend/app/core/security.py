"""
Security utilities for authentication and authorization
Enhanced with JWT token rotation, blacklisting, and security hardening
"""
import hashlib
import secrets
import uuid
from datetime import datetime, timedelta
from typing import Any, Union, Optional, Set, Dict
import redis
import structlog

from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.config import settings

# Configure structured logging
logger = structlog.get_logger()

# Password hashing with enhanced security
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12  # Increased rounds for better security
)

# JWT Security
security = HTTPBearer()

# Redis connection for token blacklisting and session management
try:
    redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    redis_client.ping()  # Test connection
    logger.info("Redis connection established for token management")
except Exception as e:
    logger.warning("Redis connection failed, token blacklisting disabled", error=str(e))
    redis_client = None

# Token blacklist and session management
class TokenManager:
    """Manages JWT tokens with blacklisting and rotation"""

    def __init__(self):
        self.redis_client = redis_client
        self.blacklist_prefix = "dealverse:blacklist:"
        self.session_prefix = "dealverse:session:"
        self.failed_attempts_prefix = "dealverse:failed_attempts:"

    def add_to_blacklist(self, token: str, expires_at: datetime) -> None:
        """Add token to blacklist"""
        if not self.redis_client:
            return

        try:
            # Calculate TTL based on token expiration
            ttl = int((expires_at - datetime.utcnow()).total_seconds())
            if ttl > 0:
                token_hash = hashlib.sha256(token.encode()).hexdigest()
                self.redis_client.setex(
                    f"{self.blacklist_prefix}{token_hash}",
                    ttl,
                    "blacklisted"
                )
                logger.info("Token added to blacklist", token_hash=token_hash[:16])
        except Exception as e:
            logger.error("Failed to blacklist token", error=str(e))

    def is_blacklisted(self, token: str) -> bool:
        """Check if token is blacklisted"""
        if not self.redis_client:
            return False

        try:
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            return self.redis_client.exists(f"{self.blacklist_prefix}{token_hash}")
        except Exception as e:
            logger.error("Failed to check token blacklist", error=str(e))
            return False

    def create_session(self, user_id: str, session_data: Dict[str, Any]) -> str:
        """Create user session with unique session ID"""
        if not self.redis_client:
            return str(uuid.uuid4())

        try:
            session_id = str(uuid.uuid4())
            session_key = f"{self.session_prefix}{user_id}:{session_id}"

            # Store session data with TTL
            self.redis_client.setex(
                session_key,
                settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,  # Same as refresh token
                str(session_data)
            )

            logger.info("Session created", user_id=user_id, session_id=session_id[:16])
            return session_id
        except Exception as e:
            logger.error("Failed to create session", error=str(e))
            return str(uuid.uuid4())

    def invalidate_session(self, user_id: str, session_id: str) -> None:
        """Invalidate specific user session"""
        if not self.redis_client:
            return

        try:
            session_key = f"{self.session_prefix}{user_id}:{session_id}"
            self.redis_client.delete(session_key)
            logger.info("Session invalidated", user_id=user_id, session_id=session_id[:16])
        except Exception as e:
            logger.error("Failed to invalidate session", error=str(e))

    def invalidate_all_sessions(self, user_id: str) -> None:
        """Invalidate all sessions for a user"""
        if not self.redis_client:
            return

        try:
            pattern = f"{self.session_prefix}{user_id}:*"
            for key in self.redis_client.scan_iter(match=pattern):
                self.redis_client.delete(key)
            logger.info("All sessions invalidated", user_id=user_id)
        except Exception as e:
            logger.error("Failed to invalidate all sessions", error=str(e))

# Initialize token manager
token_manager = TokenManager()


def create_access_token(
    subject: Union[str, Any],
    expires_delta: timedelta = None,
    session_id: Optional[str] = None,
    additional_claims: Optional[Dict[str, Any]] = None
) -> str:
    """Create JWT access token with enhanced security"""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    # Generate unique token ID for tracking
    token_id = str(uuid.uuid4())

    # Base claims
    to_encode = {
        "exp": expire,
        "iat": datetime.utcnow(),
        "sub": str(subject),
        "type": "access",
        "jti": token_id,  # JWT ID for token tracking
        "iss": settings.PROJECT_NAME,  # Issuer
    }

    # Add session ID if provided
    if session_id:
        to_encode["sid"] = session_id

    # Add additional claims if provided
    if additional_claims:
        to_encode.update(additional_claims)

    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )

    logger.info(
        "Access token created",
        user_id=str(subject),
        token_id=token_id[:16],
        expires_at=expire.isoformat()
    )

    return encoded_jwt


def create_refresh_token(
    subject: Union[str, Any],
    session_id: Optional[str] = None
) -> str:
    """Create JWT refresh token with enhanced security"""
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    # Generate unique token ID
    token_id = str(uuid.uuid4())

    to_encode = {
        "exp": expire,
        "iat": datetime.utcnow(),
        "sub": str(subject),
        "type": "refresh",
        "jti": token_id,
        "iss": settings.PROJECT_NAME,
    }

    # Add session ID if provided
    if session_id:
        to_encode["sid"] = session_id

    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )

    logger.info(
        "Refresh token created",
        user_id=str(subject),
        token_id=token_id[:16],
        expires_at=expire.isoformat()
    )

    return encoded_jwt


def verify_token(
    token: str,
    token_type: str = "access",
    check_blacklist: bool = True
) -> Optional[Dict[str, Any]]:
    """Verify JWT token and return payload with enhanced security checks"""
    try:
        # Check if token is blacklisted first
        if check_blacklist and token_manager.is_blacklisted(token):
            logger.warning("Blacklisted token used", token_hash=hashlib.sha256(token.encode()).hexdigest()[:16])
            return None

        # Decode and verify token
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            options={"verify_exp": True, "verify_iat": True}
        )

        # Validate required claims
        token_sub: str = payload.get("sub")
        token_type_claim: str = payload.get("type")
        token_id: str = payload.get("jti")
        issuer: str = payload.get("iss")

        # Check required fields
        if not all([token_sub, token_type_claim, token_id]):
            logger.warning("Token missing required claims")
            return None

        # Verify token type
        if token_type_claim != token_type:
            logger.warning("Invalid token type", expected=token_type, actual=token_type_claim)
            return None

        # Verify issuer
        if issuer != settings.PROJECT_NAME:
            logger.warning("Invalid token issuer", issuer=issuer)
            return None

        # Log successful verification
        logger.debug(
            "Token verified successfully",
            user_id=token_sub,
            token_type=token_type,
            token_id=token_id[:16]
        )

        return payload

    except jwt.ExpiredSignatureError:
        logger.warning("Expired token used")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning("Invalid token", error=str(e))
        return None
    except Exception as e:
        logger.error("Token verification error", error=str(e))
        return None


def verify_token_simple(token: str, token_type: str = "access") -> Optional[str]:
    """Simple token verification that returns only user ID (backward compatibility)"""
    payload = verify_token(token, token_type)
    return payload.get("sub") if payload else None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate password hash"""
    return pwd_context.hash(password)


def verify_access_token(credentials: HTTPAuthorizationCredentials) -> Dict[str, Any]:
    """Verify access token from Authorization header and return full payload"""
    token = credentials.credentials
    payload = verify_token(token, "access")

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return payload


def invalidate_token(token: str) -> None:
    """Invalidate a specific token by adding it to blacklist"""
    try:
        # Decode token to get expiration
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            options={"verify_exp": False}  # Don't verify expiration for blacklisting
        )

        exp_timestamp = payload.get("exp")
        if exp_timestamp:
            expires_at = datetime.fromtimestamp(exp_timestamp)
            token_manager.add_to_blacklist(token, expires_at)

            logger.info(
                "Token invalidated",
                token_id=payload.get("jti", "unknown")[:16],
                user_id=payload.get("sub")
            )
    except Exception as e:
        logger.error("Failed to invalidate token", error=str(e))


def invalidate_all_user_tokens(user_id: str) -> None:
    """Invalidate all tokens for a specific user"""
    token_manager.invalidate_all_sessions(user_id)
    logger.info("All tokens invalidated for user", user_id=user_id)


def create_secure_session(user_id: str, user_agent: str = None, ip_address: str = None) -> str:
    """Create a secure session with metadata"""
    session_data = {
        "user_id": user_id,
        "created_at": datetime.utcnow().isoformat(),
        "user_agent": user_agent or "unknown",
        "ip_address": ip_address or "unknown",
        "last_activity": datetime.utcnow().isoformat()
    }

    return token_manager.create_session(user_id, session_data)


# Role-based access control
class RoleChecker:
    """Check user roles for authorization"""
    
    def __init__(self, allowed_roles: list):
        self.allowed_roles = allowed_roles
    
    def __call__(self, user_role: str):
        if user_role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operation not permitted"
            )


# Permission definitions
PERMISSIONS = {
    "admin": [
        "deals:all",
        "users:all", 
        "organizations:all",
        "analytics:all",
        "compliance:all"
    ],
    "manager": [
        "deals:read",
        "deals:create",
        "deals:edit",
        "users:read",
        "analytics:read",
        "compliance:read"
    ],
    "analyst": [
        "deals:read",
        "deals:create",
        "models:create",
        "models:edit_own",
        "documents:read",
        "documents:upload"
    ],
    "associate": [
        "deals:read",
        "deals:edit",
        "models:create", 
        "models:edit_all",
        "documents:read",
        "documents:upload",
        "documents:analyze"
    ],
    "vp": [
        "deals:create",
        "deals:edit",
        "deals:delete",
        "team:manage",
        "models:approve",
        "compliance:review"
    ]
}


# Rate limiting and security monitoring
class SecurityMonitor:
    """Monitor and track security events"""

    def __init__(self):
        self.redis_client = redis_client

    def track_failed_attempt(self, identifier: str, attempt_type: str = "login") -> int:
        """Track failed authentication attempt"""
        if not self.redis_client:
            return 0

        try:
            key = f"{token_manager.failed_attempts_prefix}{attempt_type}:{identifier}"
            attempts = self.redis_client.incr(key)

            # Set expiration for failed attempts (15 minutes)
            if attempts == 1:
                self.redis_client.expire(key, 900)

            logger.warning(
                "Failed authentication attempt",
                identifier=identifier,
                attempt_type=attempt_type,
                attempts=attempts
            )

            return attempts
        except Exception as e:
            logger.error("Failed to track failed attempt", error=str(e))
            return 0

    def get_failed_attempts(self, identifier: str, attempt_type: str = "login") -> int:
        """Get number of failed attempts for identifier"""
        if not self.redis_client:
            return 0

        try:
            key = f"{token_manager.failed_attempts_prefix}{attempt_type}:{identifier}"
            attempts = self.redis_client.get(key)
            return int(attempts) if attempts else 0
        except Exception as e:
            logger.error("Failed to get failed attempts", error=str(e))
            return 0

    def clear_failed_attempts(self, identifier: str, attempt_type: str = "login") -> None:
        """Clear failed attempts for identifier"""
        if not self.redis_client:
            return

        try:
            key = f"{token_manager.failed_attempts_prefix}{attempt_type}:{identifier}"
            self.redis_client.delete(key)
            logger.info("Failed attempts cleared", identifier=identifier, attempt_type=attempt_type)
        except Exception as e:
            logger.error("Failed to clear failed attempts", error=str(e))

    def is_account_locked(self, identifier: str, max_attempts: int = 5) -> bool:
        """Check if account is locked due to failed attempts"""
        attempts = self.get_failed_attempts(identifier)
        return attempts >= max_attempts

# Initialize security monitor
security_monitor = SecurityMonitor()


def check_permission(user_role: str, required_permission: str) -> bool:
    """Check if user role has required permission"""
    user_permissions = PERMISSIONS.get(user_role, [])
    return required_permission in user_permissions or "all" in user_permissions


# Enhanced password security
def validate_password_strength(password: str) -> Dict[str, Any]:
    """Validate password strength and return detailed feedback"""
    result = {
        "is_valid": True,
        "score": 0,
        "feedback": [],
        "requirements_met": {
            "length": False,
            "uppercase": False,
            "lowercase": False,
            "numbers": False,
            "special_chars": False,
            "no_common_patterns": False
        }
    }

    # Check length
    if len(password) >= 12:
        result["score"] += 2
        result["requirements_met"]["length"] = True
    elif len(password) >= 8:
        result["score"] += 1
    else:
        result["is_valid"] = False
        result["feedback"].append("Password must be at least 8 characters long")

    # Check character types
    if any(c.isupper() for c in password):
        result["score"] += 1
        result["requirements_met"]["uppercase"] = True
    else:
        result["feedback"].append("Password must contain at least one uppercase letter")

    if any(c.islower() for c in password):
        result["score"] += 1
        result["requirements_met"]["lowercase"] = True
    else:
        result["feedback"].append("Password must contain at least one lowercase letter")

    if any(c.isdigit() for c in password):
        result["score"] += 1
        result["requirements_met"]["numbers"] = True
    else:
        result["feedback"].append("Password must contain at least one number")

    if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        result["score"] += 1
        result["requirements_met"]["special_chars"] = True
    else:
        result["feedback"].append("Password must contain at least one special character")

    # Check for common patterns
    common_patterns = ["123", "abc", "password", "admin", "user"]
    if not any(pattern in password.lower() for pattern in common_patterns):
        result["score"] += 1
        result["requirements_met"]["no_common_patterns"] = True
    else:
        result["feedback"].append("Password contains common patterns")

    # Final validation
    if result["score"] < 4:
        result["is_valid"] = False

    return result
