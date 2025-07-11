"""
Cache Middleware for FastAPI
Provides automatic response caching for API endpoints
"""
import json
import hashlib
from typing import Callable, Optional, Set
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import logging

from app.services.cache_service import cache_service

logger = logging.getLogger(__name__)


class CacheMiddleware(BaseHTTPMiddleware):
    """Middleware for automatic API response caching"""
    
    def __init__(
        self,
        app,
        default_ttl: int = 300,
        cache_methods: Set[str] = None,
        exclude_paths: Set[str] = None,
        cache_headers: bool = True
    ):
        super().__init__(app)
        self.default_ttl = default_ttl
        self.cache_methods = cache_methods or {"GET"}
        self.exclude_paths = exclude_paths or {
            "/docs", "/redoc", "/openapi.json", "/health", "/metrics"
        }
        self.cache_headers = cache_headers
    
    def _should_cache_request(self, request: Request) -> bool:
        """Determine if request should be cached"""
        # Only cache specified HTTP methods
        if request.method not in self.cache_methods:
            return False
        
        # Skip excluded paths
        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            return False
        
        # Skip if cache is disabled
        if not cache_service.is_available():
            return False
        
        # Skip if no-cache header is present
        if request.headers.get("cache-control") == "no-cache":
            return False
        
        return True
    
    def _generate_cache_key(self, request: Request) -> str:
        """Generate cache key for request"""
        # Include method, path, query params, and user context
        key_components = [
            request.method,
            request.url.path,
            str(sorted(request.query_params.items())),
        ]
        
        # Include user ID if available for user-specific caching
        user_id = getattr(request.state, "user_id", None)
        if user_id:
            key_components.append(f"user:{user_id}")
        
        # Include organization ID if available
        org_id = getattr(request.state, "organization_id", None)
        if org_id:
            key_components.append(f"org:{org_id}")
        
        key_string = ":".join(key_components)
        key_hash = hashlib.md5(key_string.encode()).hexdigest()
        
        return f"dealverse:api:{key_hash}"
    
    def _get_ttl_for_path(self, path: str) -> int:
        """Get TTL based on endpoint path"""
        # Different TTL for different types of endpoints
        ttl_mapping = {
            "/api/v1/deals": 180,  # 3 minutes for deals
            "/api/v1/clients": 300,  # 5 minutes for clients
            "/api/v1/users": 600,  # 10 minutes for users
            "/api/v1/organizations": 1800,  # 30 minutes for organizations
            "/api/v1/dashboard": 120,  # 2 minutes for dashboard
            "/api/v1/analytics": 300,  # 5 minutes for analytics
            "/api/v1/documents": 240,  # 4 minutes for documents
            "/api/v1/tasks": 180,  # 3 minutes for tasks
        }
        
        # Find matching path
        for path_prefix, ttl in ttl_mapping.items():
            if path.startswith(path_prefix):
                return ttl
        
        return self.default_ttl
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with caching"""
        
        # Check if we should cache this request
        if not self._should_cache_request(request):
            return await call_next(request)
        
        # Generate cache key
        cache_key = self._generate_cache_key(request)
        
        # Try to get cached response
        cached_response = cache_service.get(cache_key)
        if cached_response is not None:
            logger.debug(f"Cache hit for {request.method} {request.url.path}")
            
            # Return cached response
            response = JSONResponse(
                content=cached_response["content"],
                status_code=cached_response["status_code"],
                headers=cached_response.get("headers", {})
            )
            
            # Add cache headers
            if self.cache_headers:
                response.headers["X-Cache"] = "HIT"
                response.headers["X-Cache-Key"] = cache_key
            
            return response
        
        # Process request
        response = await call_next(request)
        
        # Cache successful responses
        if response.status_code == 200 and hasattr(response, "body"):
            try:
                # Get response content
                response_body = response.body
                if response_body:
                    content = json.loads(response_body.decode())
                    
                    # Prepare cache data
                    cache_data = {
                        "content": content,
                        "status_code": response.status_code,
                        "headers": dict(response.headers) if self.cache_headers else {}
                    }
                    
                    # Get TTL for this path
                    ttl = self._get_ttl_for_path(request.url.path)
                    
                    # Cache the response
                    cache_service.set(cache_key, cache_data, ttl=ttl)
                    logger.debug(f"Cached response for {request.method} {request.url.path} (TTL: {ttl}s)")
                    
                    # Add cache headers
                    if self.cache_headers:
                        response.headers["X-Cache"] = "MISS"
                        response.headers["X-Cache-Key"] = cache_key
                        response.headers["X-Cache-TTL"] = str(ttl)
            
            except Exception as e:
                logger.error(f"Error caching response: {e}")
        
        return response


class CacheInvalidationMiddleware(BaseHTTPMiddleware):
    """Middleware for automatic cache invalidation on data changes"""
    
    def __init__(self, app):
        super().__init__(app)
        self.invalidation_patterns = {
            # Deal-related invalidations
            "/api/v1/deals": ["dealverse:api:*deals*", "dealverse:api:*dashboard*"],
            "/api/v1/clients": ["dealverse:api:*clients*", "dealverse:api:*dashboard*"],
            "/api/v1/users": ["dealverse:api:*users*"],
            "/api/v1/documents": ["dealverse:api:*documents*", "dealverse:api:*dashboard*"],
            "/api/v1/tasks": ["dealverse:api:*tasks*", "dealverse:api:*dashboard*"],
            "/api/v1/financial-models": ["dealverse:api:*financial*", "dealverse:api:*dashboard*"],
        }
    
    def _should_invalidate_cache(self, request: Request) -> bool:
        """Determine if cache should be invalidated"""
        # Invalidate on data-changing operations
        return request.method in {"POST", "PUT", "PATCH", "DELETE"}
    
    def _get_invalidation_patterns(self, path: str) -> list:
        """Get cache invalidation patterns for a path"""
        patterns = []
        for path_prefix, cache_patterns in self.invalidation_patterns.items():
            if path.startswith(path_prefix):
                patterns.extend(cache_patterns)
        
        # Always invalidate dashboard cache on any data change
        if not any("dashboard" in pattern for pattern in patterns):
            patterns.append("dealverse:api:*dashboard*")
        
        return patterns
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with cache invalidation"""
        
        # Process the request first
        response = await call_next(request)
        
        # Invalidate cache if needed
        if (self._should_invalidate_cache(request) and 
            response.status_code in {200, 201, 204} and
            cache_service.is_available()):
            
            patterns = self._get_invalidation_patterns(request.url.path)
            
            total_invalidated = 0
            for pattern in patterns:
                invalidated = cache_service.delete_pattern(pattern)
                total_invalidated += invalidated
            
            if total_invalidated > 0:
                logger.info(f"Invalidated {total_invalidated} cache entries for {request.method} {request.url.path}")
        
        return response


def cache_response(ttl: int = 300, key_prefix: str = "api"):
    """
    Decorator for manual response caching
    
    Args:
        ttl: Time to live in seconds
        key_prefix: Prefix for cache key
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Extract request info for cache key
            request = kwargs.get("request") or (args[0] if args else None)
            if not request or not hasattr(request, "url"):
                return await func(*args, **kwargs)
            
            # Generate cache key
            cache_key = cache_service._generate_key(
                key_prefix, 
                func.__name__, 
                request.url.path,
                str(sorted(request.query_params.items()))
            )
            
            # Try cache first
            cached_result = cache_service.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            cache_service.set(cache_key, result, ttl=ttl)
            
            return result
        
        return wrapper
    return decorator


def invalidate_cache_on_change(patterns: list):
    """
    Decorator for cache invalidation on data changes
    
    Args:
        patterns: List of cache key patterns to invalidate
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Execute function first
            result = await func(*args, **kwargs)
            
            # Invalidate cache patterns
            if cache_service.is_available():
                total_invalidated = 0
                for pattern in patterns:
                    invalidated = cache_service.delete_pattern(pattern)
                    total_invalidated += invalidated
                
                if total_invalidated > 0:
                    logger.info(f"Invalidated {total_invalidated} cache entries for {func.__name__}")
            
            return result
        
        return wrapper
    return decorator
