"""
Redis Cache Service for DealVerse OS
Provides centralized caching with TTL management and invalidation patterns
"""
import json
import pickle
import hashlib
from typing import Any, Dict, List, Optional, Union, Callable
from datetime import datetime, timedelta
from functools import wraps
import redis
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class CacheService:
    """Centralized Redis cache service with advanced features"""
    
    def __init__(self):
        """Initialize Redis connection"""
        try:
            self.redis_client = redis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30
            )
            # Test connection
            self.redis_client.ping()
            logger.info("Redis cache service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Redis cache service: {e}")
            self.redis_client = None
    
    def is_available(self) -> bool:
        """Check if Redis is available"""
        if not self.redis_client:
            return False
        try:
            self.redis_client.ping()
            return True
        except Exception:
            return False
    
    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate a consistent cache key"""
        # Create a hash of the arguments for consistent key generation
        key_data = f"{prefix}:{args}:{sorted(kwargs.items())}"
        key_hash = hashlib.md5(key_data.encode()).hexdigest()
        return f"dealverse:{prefix}:{key_hash}"
    
    def set(
        self, 
        key: str, 
        value: Any, 
        ttl: Optional[int] = None,
        serialize: bool = True
    ) -> bool:
        """Set a value in cache with optional TTL"""
        if not self.is_available():
            return False
        
        try:
            # Serialize complex objects
            if serialize and not isinstance(value, (str, int, float, bool)):
                if isinstance(value, (dict, list)):
                    value = json.dumps(value, default=str)
                else:
                    value = pickle.dumps(value)
            
            if ttl:
                return self.redis_client.setex(key, ttl, value)
            else:
                return self.redis_client.set(key, value)
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False
    
    def get(self, key: str, deserialize: bool = True) -> Optional[Any]:
        """Get a value from cache"""
        if not self.is_available():
            return None
        
        try:
            value = self.redis_client.get(key)
            if value is None:
                return None
            
            # Try to deserialize
            if deserialize:
                try:
                    # Try JSON first
                    return json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    try:
                        # Try pickle
                        return pickle.loads(value)
                    except (pickle.PickleError, TypeError):
                        # Return as string
                        return value
            
            return value
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            return None
    
    def delete(self, key: str) -> bool:
        """Delete a key from cache"""
        if not self.is_available():
            return False
        
        try:
            return bool(self.redis_client.delete(key))
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False
    
    def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching a pattern"""
        if not self.is_available():
            return 0
        
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Cache delete pattern error for pattern {pattern}: {e}")
            return 0
    
    def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        if not self.is_available():
            return False
        
        try:
            return bool(self.redis_client.exists(key))
        except Exception as e:
            logger.error(f"Cache exists error for key {key}: {e}")
            return False
    
    def ttl(self, key: str) -> int:
        """Get TTL for a key"""
        if not self.is_available():
            return -1
        
        try:
            return self.redis_client.ttl(key)
        except Exception as e:
            logger.error(f"Cache TTL error for key {key}: {e}")
            return -1
    
    def increment(self, key: str, amount: int = 1, ttl: Optional[int] = None) -> Optional[int]:
        """Increment a counter"""
        if not self.is_available():
            return None
        
        try:
            value = self.redis_client.incr(key, amount)
            if ttl and value == amount:  # First time setting
                self.redis_client.expire(key, ttl)
            return value
        except Exception as e:
            logger.error(f"Cache increment error for key {key}: {e}")
            return None
    
    def set_hash(self, key: str, mapping: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """Set a hash in cache"""
        if not self.is_available():
            return False
        
        try:
            # Serialize values in the hash
            serialized_mapping = {}
            for k, v in mapping.items():
                if isinstance(v, (dict, list)):
                    serialized_mapping[k] = json.dumps(v, default=str)
                elif not isinstance(v, (str, int, float, bool)):
                    serialized_mapping[k] = pickle.dumps(v)
                else:
                    serialized_mapping[k] = v
            
            result = self.redis_client.hset(key, mapping=serialized_mapping)
            if ttl:
                self.redis_client.expire(key, ttl)
            return bool(result)
        except Exception as e:
            logger.error(f"Cache set hash error for key {key}: {e}")
            return False
    
    def get_hash(self, key: str, field: Optional[str] = None) -> Optional[Any]:
        """Get a hash or hash field from cache"""
        if not self.is_available():
            return None
        
        try:
            if field:
                value = self.redis_client.hget(key, field)
                if value is None:
                    return None
                
                # Try to deserialize
                try:
                    return json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    try:
                        return pickle.loads(value)
                    except (pickle.PickleError, TypeError):
                        return value
            else:
                hash_data = self.redis_client.hgetall(key)
                if not hash_data:
                    return None
                
                # Deserialize all values
                result = {}
                for k, v in hash_data.items():
                    try:
                        result[k] = json.loads(v)
                    except (json.JSONDecodeError, TypeError):
                        try:
                            result[k] = pickle.loads(v)
                        except (pickle.PickleError, TypeError):
                            result[k] = v
                
                return result
        except Exception as e:
            logger.error(f"Cache get hash error for key {key}: {e}")
            return None
    
    def invalidate_organization_cache(self, organization_id: str):
        """Invalidate all cache entries for an organization"""
        patterns = [
            f"dealverse:deals:*{organization_id}*",
            f"dealverse:clients:*{organization_id}*",
            f"dealverse:documents:*{organization_id}*",
            f"dealverse:tasks:*{organization_id}*",
            f"dealverse:users:*{organization_id}*",
            f"dealverse:dashboard:*{organization_id}*",
            f"dealverse:analytics:*{organization_id}*"
        ]
        
        total_deleted = 0
        for pattern in patterns:
            deleted = self.delete_pattern(pattern)
            total_deleted += deleted
            logger.info(f"Invalidated {deleted} cache entries for pattern: {pattern}")
        
        logger.info(f"Total cache entries invalidated for organization {organization_id}: {total_deleted}")
        return total_deleted
    
    def invalidate_user_cache(self, user_id: str):
        """Invalidate all cache entries for a user"""
        patterns = [
            f"dealverse:user:*{user_id}*",
            f"dealverse:auth:*{user_id}*",
            f"dealverse:permissions:*{user_id}*"
        ]
        
        total_deleted = 0
        for pattern in patterns:
            deleted = self.delete_pattern(pattern)
            total_deleted += deleted
        
        logger.info(f"Total cache entries invalidated for user {user_id}: {total_deleted}")
        return total_deleted


# Global cache service instance
cache_service = CacheService()


def cached(
    ttl: int = 300,
    key_prefix: str = "default",
    invalidate_on: Optional[List[str]] = None
):
    """
    Decorator for caching function results
    
    Args:
        ttl: Time to live in seconds
        key_prefix: Prefix for cache key
        invalidate_on: List of events that should invalidate this cache
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = cache_service._generate_key(key_prefix, func.__name__, *args, **kwargs)
            
            # Try to get from cache
            cached_result = cache_service.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for key: {cache_key}")
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache_service.set(cache_key, result, ttl=ttl)
            logger.debug(f"Cache miss, stored result for key: {cache_key}")
            
            return result
        
        return wrapper
    return decorator
