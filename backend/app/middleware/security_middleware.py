"""
Security middleware for enhanced application security
"""
import time
from typing import Callable
from fastapi import Request, Response
from fastapi.responses import JSONResponse
import structlog

from app.core.config import settings

logger = structlog.get_logger()


class SecurityHeadersMiddleware:
    """Add security headers to all responses"""
    
    def __init__(self, app: Callable):
        self.app = app
    
    async def __call__(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        if settings.SECURITY_HEADERS_ENABLED:
            # Security headers
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-XSS-Protection"] = "1; mode=block"
            response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
            response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
            
            # Content Security Policy
            if settings.CONTENT_SECURITY_POLICY:
                response.headers["Content-Security-Policy"] = settings.CONTENT_SECURITY_POLICY
            
            # HSTS (only in production)
            if settings.ENVIRONMENT == "production":
                response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
        
        return response


class RateLimitMiddleware:
    """Rate limiting middleware to prevent abuse"""
    
    def __init__(self, app: Callable):
        self.app = app
        self.request_counts = {}  # In production, use Redis
        self.window_size = 60  # 1 minute window
        
    async def __call__(self, request: Request, call_next: Callable) -> Response:
        # Get client identifier
        client_ip = request.client.host if request.client else "unknown"
        current_time = int(time.time())
        window_start = current_time - (current_time % self.window_size)
        
        # Create key for this client and time window
        key = f"{client_ip}:{window_start}"
        
        # Count requests in current window
        if key not in self.request_counts:
            self.request_counts[key] = 0
        
        self.request_counts[key] += 1
        
        # Clean old entries
        self._cleanup_old_entries(current_time)
        
        # Check rate limit
        if self.request_counts[key] > settings.RATE_LIMIT_PER_MINUTE:
            logger.warning(
                "Rate limit exceeded",
                client_ip=client_ip,
                requests=self.request_counts[key],
                limit=settings.RATE_LIMIT_PER_MINUTE
            )
            
            return JSONResponse(
                status_code=429,
                content={
                    "success": False,
                    "message": "Rate limit exceeded",
                    "detail": f"Maximum {settings.RATE_LIMIT_PER_MINUTE} requests per minute allowed"
                },
                headers={
                    "Retry-After": str(self.window_size),
                    "X-RateLimit-Limit": str(settings.RATE_LIMIT_PER_MINUTE),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(window_start + self.window_size)
                }
            )
        
        # Add rate limit headers to response
        response = await call_next(request)
        remaining = max(0, settings.RATE_LIMIT_PER_MINUTE - self.request_counts[key])
        
        response.headers["X-RateLimit-Limit"] = str(settings.RATE_LIMIT_PER_MINUTE)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(window_start + self.window_size)
        
        return response
    
    def _cleanup_old_entries(self, current_time: int):
        """Remove old rate limit entries"""
        cutoff_time = current_time - self.window_size * 2  # Keep 2 windows
        keys_to_remove = []
        
        for key in self.request_counts:
            try:
                window_time = int(key.split(':')[1])
                if window_time < cutoff_time:
                    keys_to_remove.append(key)
            except (IndexError, ValueError):
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self.request_counts[key]


class RequestValidationMiddleware:
    """Validate and sanitize incoming requests"""
    
    def __init__(self, app: Callable):
        self.app = app
        self.max_request_size = 50 * 1024 * 1024  # 50MB
        self.suspicious_patterns = [
            # SQL injection patterns
            r"(\bunion\b.*\bselect\b)",
            r"(\bselect\b.*\bfrom\b)",
            r"(\binsert\b.*\binto\b)",
            r"(\bdelete\b.*\bfrom\b)",
            r"(\bdrop\b.*\btable\b)",
            
            # XSS patterns
            r"<script[^>]*>",
            r"javascript:",
            r"on\w+\s*=",
            
            # Path traversal
            r"\.\./",
            r"\.\.\\",
        ]
    
    async def __call__(self, request: Request, call_next: Callable) -> Response:
        # Check request size
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > self.max_request_size:
            logger.warning(
                "Request size too large",
                content_length=content_length,
                max_size=self.max_request_size,
                client_ip=request.client.host if request.client else "unknown"
            )
            
            return JSONResponse(
                status_code=413,
                content={
                    "success": False,
                    "message": "Request entity too large",
                    "detail": f"Maximum request size is {self.max_request_size} bytes"
                }
            )
        
        # Validate URL and headers for suspicious patterns
        url_str = str(request.url)
        user_agent = request.headers.get("user-agent", "")
        
        # Check for suspicious patterns (basic implementation)
        for pattern in self.suspicious_patterns:
            import re
            if re.search(pattern, url_str, re.IGNORECASE) or re.search(pattern, user_agent, re.IGNORECASE):
                logger.warning(
                    "Suspicious request detected",
                    pattern=pattern,
                    url=url_str,
                    user_agent=user_agent,
                    client_ip=request.client.host if request.client else "unknown"
                )
                
                return JSONResponse(
                    status_code=400,
                    content={
                        "success": False,
                        "message": "Invalid request",
                        "detail": "Request contains suspicious patterns"
                    }
                )
        
        return await call_next(request)


class AuditLoggingMiddleware:
    """Log security-relevant events for audit purposes"""
    
    def __init__(self, app: Callable):
        self.app = app
        self.sensitive_endpoints = {
            "/api/v1/auth/login",
            "/api/v1/auth/login/json",
            "/api/v1/auth/refresh",
            "/api/v1/auth/logout",
            "/api/v1/auth/change-password",
            "/api/v1/users",
            "/api/v1/organizations"
        }
    
    async def __call__(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        # Check if this is a sensitive endpoint
        is_sensitive = any(request.url.path.startswith(endpoint) for endpoint in self.sensitive_endpoints)
        
        if is_sensitive and settings.AUDIT_LOG_ENABLED:
            # Log request details
            logger.info(
                "Audit: Sensitive endpoint accessed",
                method=request.method,
                path=request.url.path,
                client_ip=request.client.host if request.client else "unknown",
                user_agent=request.headers.get("user-agent", "unknown"),
                timestamp=time.time()
            )
        
        # Process request
        response = await call_next(request)
        
        if is_sensitive and settings.AUDIT_LOG_ENABLED:
            # Log response details
            process_time = time.time() - start_time
            logger.info(
                "Audit: Sensitive endpoint response",
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                process_time=round(process_time, 4),
                client_ip=request.client.host if request.client else "unknown"
            )
        
        return response
