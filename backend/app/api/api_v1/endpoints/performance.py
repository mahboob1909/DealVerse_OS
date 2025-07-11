"""
Performance monitoring endpoints
"""
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api import deps
from app.db.database import get_db
from app.models.user import User
from app.middleware.performance_middleware import (
    get_performance_metrics,
    get_endpoint_metrics,
    reset_performance_metrics
)
from app.services.cache_service import cache_service
from app.db.database import check_database_health, get_connection_pool_status

router = APIRouter()


@router.get("/metrics")
def get_system_performance_metrics(
    current_user: User = Depends(deps.check_permission("analytics:read")),
) -> Any:
    """
    Get comprehensive system performance metrics
    """
    metrics = get_performance_metrics()
    
    if not metrics:
        return {
            "message": "No performance metrics available",
            "total_requests": 0,
            "avg_response_time": 0,
            "error_rate": 0,
            "endpoints": {}
        }
    
    # Calculate additional metrics
    error_rate = 0
    if metrics.get("total_requests", 0) > 0:
        error_rate = (metrics.get("error_count", 0) / metrics["total_requests"]) * 100
    
    return {
        "total_requests": metrics.get("total_requests", 0),
        "avg_response_time": round(metrics.get("avg_response_time", 0), 2),
        "max_response_time": round(metrics.get("max_response_time", 0), 2),
        "min_response_time": round(metrics.get("min_response_time", 0), 2),
        "avg_request_size": metrics.get("avg_request_size", 0),
        "avg_response_size": metrics.get("avg_response_size", 0),
        "error_count": metrics.get("error_count", 0),
        "error_rate": round(error_rate, 2),
        "endpoints": metrics.get("endpoints", {})
    }


@router.get("/metrics/endpoints")
def get_endpoint_performance_metrics(
    endpoint: Optional[str] = Query(None, description="Specific endpoint to get metrics for"),
    current_user: User = Depends(deps.check_permission("analytics:read")),
) -> Any:
    """
    Get performance metrics for specific endpoints
    """
    if endpoint:
        metrics = get_endpoint_metrics(endpoint)
        if not metrics:
            return {"message": f"No metrics found for endpoint: {endpoint}"}
        return {
            "endpoint": endpoint,
            "metrics": metrics
        }
    
    # Return all endpoint metrics
    all_metrics = get_endpoint_metrics()
    
    # Sort by request count (most used endpoints first)
    sorted_endpoints = sorted(
        all_metrics.items(),
        key=lambda x: x[1].get("count", 0),
        reverse=True
    )
    
    return {
        "endpoints": dict(sorted_endpoints),
        "total_endpoints": len(all_metrics)
    }


@router.get("/metrics/slow-endpoints")
def get_slow_endpoints(
    threshold: float = Query(1000, description="Response time threshold in milliseconds"),
    limit: int = Query(10, description="Number of slow endpoints to return"),
    current_user: User = Depends(deps.check_permission("analytics:read")),
) -> Any:
    """
    Get endpoints with response times above threshold
    """
    all_metrics = get_endpoint_metrics()
    
    # Filter endpoints above threshold
    slow_endpoints = []
    for endpoint, metrics in all_metrics.items():
        avg_time = metrics.get("avg_time", 0)
        if avg_time > threshold:
            slow_endpoints.append({
                "endpoint": endpoint,
                "avg_response_time": round(avg_time, 2),
                "request_count": metrics.get("count", 0),
                "error_count": metrics.get("errors", 0),
                "error_rate": round((metrics.get("errors", 0) / max(metrics.get("count", 1), 1)) * 100, 2)
            })
    
    # Sort by average response time (slowest first)
    slow_endpoints.sort(key=lambda x: x["avg_response_time"], reverse=True)
    
    return {
        "threshold_ms": threshold,
        "slow_endpoints": slow_endpoints[:limit],
        "total_slow_endpoints": len(slow_endpoints)
    }


@router.get("/metrics/errors")
def get_error_metrics(
    current_user: User = Depends(deps.check_permission("analytics:read")),
) -> Any:
    """
    Get error metrics and endpoints with high error rates
    """
    all_metrics = get_endpoint_metrics()
    
    error_endpoints = []
    total_errors = 0
    total_requests = 0
    
    for endpoint, metrics in all_metrics.items():
        errors = metrics.get("errors", 0)
        count = metrics.get("count", 0)
        
        total_errors += errors
        total_requests += count
        
        if errors > 0:
            error_rate = (errors / max(count, 1)) * 100
            error_endpoints.append({
                "endpoint": endpoint,
                "error_count": errors,
                "total_requests": count,
                "error_rate": round(error_rate, 2),
                "avg_response_time": round(metrics.get("avg_time", 0), 2)
            })
    
    # Sort by error rate (highest first)
    error_endpoints.sort(key=lambda x: x["error_rate"], reverse=True)
    
    overall_error_rate = (total_errors / max(total_requests, 1)) * 100
    
    return {
        "overall_error_rate": round(overall_error_rate, 2),
        "total_errors": total_errors,
        "total_requests": total_requests,
        "error_endpoints": error_endpoints
    }


@router.get("/metrics/cache")
def get_cache_metrics(
    current_user: User = Depends(deps.check_permission("analytics:read")),
) -> Any:
    """
    Get cache performance metrics
    """
    if not cache_service.is_available():
        return {"message": "Cache service not available"}
    
    try:
        # Get Redis info
        redis_info = cache_service.redis_client.info()
        
        # Extract relevant metrics
        cache_metrics = {
            "redis_version": redis_info.get("redis_version", "unknown"),
            "connected_clients": redis_info.get("connected_clients", 0),
            "used_memory": redis_info.get("used_memory", 0),
            "used_memory_human": redis_info.get("used_memory_human", "0B"),
            "used_memory_peak": redis_info.get("used_memory_peak", 0),
            "used_memory_peak_human": redis_info.get("used_memory_peak_human", "0B"),
            "keyspace_hits": redis_info.get("keyspace_hits", 0),
            "keyspace_misses": redis_info.get("keyspace_misses", 0),
            "total_commands_processed": redis_info.get("total_commands_processed", 0),
            "instantaneous_ops_per_sec": redis_info.get("instantaneous_ops_per_sec", 0),
        }
        
        # Calculate hit rate
        hits = cache_metrics["keyspace_hits"]
        misses = cache_metrics["keyspace_misses"]
        total_operations = hits + misses
        
        if total_operations > 0:
            cache_metrics["hit_rate"] = round((hits / total_operations) * 100, 2)
        else:
            cache_metrics["hit_rate"] = 0
        
        # Get key count by pattern
        dealverse_keys = len(cache_service.redis_client.keys("dealverse:*"))
        cache_metrics["dealverse_keys"] = dealverse_keys
        
        return cache_metrics
        
    except Exception as e:
        return {"error": f"Failed to get cache metrics: {str(e)}"}


@router.post("/metrics/reset")
def reset_metrics(
    current_user: User = Depends(deps.check_permission("analytics:all")),
) -> Any:
    """
    Reset all performance metrics (admin only)
    """
    try:
        reset_performance_metrics()
        return {"message": "Performance metrics reset successfully"}
    except Exception as e:
        return {"error": f"Failed to reset metrics: {str(e)}"}


@router.get("/health")
def health_check() -> Any:
    """
    Health check endpoint with basic system status
    """
    import psutil
    import time
    
    try:
        # System metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Cache status
        cache_status = "available" if cache_service.is_available() else "unavailable"
        
        # Database status (simple check)
        db_status = "available"  # Simplified for now
        
        return {
            "status": "healthy",
            "timestamp": int(time.time()),
            "system": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available": memory.available,
                "disk_percent": (disk.used / disk.total) * 100,
                "disk_free": disk.free
            },
            "services": {
                "cache": cache_status,
                "database": db_status
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": int(time.time())
        }


@router.get("/database/health")
def get_database_health(
    current_user: User = Depends(deps.check_permission("analytics:read")),
) -> Any:
    """
    Get database connection health and pool status
    """
    return check_database_health()


@router.get("/database/pool")
def get_database_pool_status(
    current_user: User = Depends(deps.check_permission("analytics:read")),
) -> Any:
    """
    Get detailed database connection pool status
    """
    try:
        pool_status = get_connection_pool_status()

        # Calculate utilization percentages
        total_capacity = pool_status["pool_size"] + pool_status["max_overflow"]
        utilization = (pool_status["checked_out_connections"] / total_capacity) * 100 if total_capacity > 0 else 0

        pool_status["utilization_percent"] = round(utilization, 2)
        pool_status["available_connections"] = total_capacity - pool_status["checked_out_connections"]

        # Add health indicators
        health_status = "healthy"
        warnings = []

        if utilization > 80:
            health_status = "warning"
            warnings.append("High connection pool utilization")

        if pool_status["invalid_connections"] > 0:
            health_status = "warning"
            warnings.append("Invalid connections detected")

        if utilization > 95:
            health_status = "critical"
            warnings.append("Connection pool near capacity")

        return {
            "health_status": health_status,
            "warnings": warnings,
            "pool_metrics": pool_status,
            "timestamp": int(time.time())
        }

    except Exception as e:
        return {
            "health_status": "error",
            "error": str(e),
            "timestamp": int(time.time())
        }
