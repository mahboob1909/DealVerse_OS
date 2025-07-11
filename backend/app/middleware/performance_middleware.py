"""
Performance Monitoring Middleware
Tracks API performance metrics, request/response sizes, and processing times
"""
import time
import sys
import psutil
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import logging

from app.services.cache_service import cache_service

logger = logging.getLogger(__name__)


class PerformanceMonitoringMiddleware(BaseHTTPMiddleware):
    """Middleware for tracking API performance metrics"""
    
    def __init__(self, app):
        super().__init__(app)
        self.process = psutil.Process()
    
    def _get_request_size(self, request: Request) -> int:
        """Calculate request size in bytes"""
        size = 0
        
        # Headers size
        if hasattr(request, 'headers'):
            for key, value in request.headers.items():
                size += len(key.encode('utf-8')) + len(value.encode('utf-8'))
        
        # URL size
        size += len(str(request.url).encode('utf-8'))
        
        # Method size
        size += len(request.method.encode('utf-8'))
        
        return size
    
    def _get_response_size(self, response: Response) -> int:
        """Calculate response size in bytes"""
        size = 0
        
        # Headers size
        if hasattr(response, 'headers'):
            for key, value in response.headers.items():
                size += len(key.encode('utf-8')) + len(value.encode('utf-8'))
        
        # Body size
        if hasattr(response, 'body') and response.body:
            size += len(response.body)
        
        return size
    
    def _get_memory_usage(self) -> dict:
        """Get current memory usage"""
        try:
            memory_info = self.process.memory_info()
            return {
                "rss": memory_info.rss,  # Resident Set Size
                "vms": memory_info.vms,  # Virtual Memory Size
                "percent": self.process.memory_percent()
            }
        except Exception:
            return {"rss": 0, "vms": 0, "percent": 0}
    
    def _get_cpu_usage(self) -> float:
        """Get current CPU usage"""
        try:
            return self.process.cpu_percent()
        except Exception:
            return 0.0
    
    def _store_metrics(self, metrics: dict):
        """Store performance metrics in cache"""
        if not cache_service.is_available():
            return
        
        try:
            # Store individual metric
            timestamp = int(time.time())
            metric_key = f"dealverse:metrics:{timestamp}"
            cache_service.set(metric_key, metrics, ttl=3600)  # Store for 1 hour
            
            # Update aggregated metrics
            self._update_aggregated_metrics(metrics)
            
        except Exception as e:
            logger.error(f"Error storing performance metrics: {e}")
    
    def _update_aggregated_metrics(self, metrics: dict):
        """Update aggregated performance metrics"""
        try:
            # Get current aggregated metrics
            agg_key = "dealverse:metrics:aggregated"
            current_agg = cache_service.get(agg_key) or {
                "total_requests": 0,
                "total_response_time": 0,
                "total_request_size": 0,
                "total_response_size": 0,
                "avg_response_time": 0,
                "avg_request_size": 0,
                "avg_response_size": 0,
                "max_response_time": 0,
                "min_response_time": float('inf'),
                "error_count": 0,
                "endpoints": {}
            }
            
            # Update counters
            current_agg["total_requests"] += 1
            current_agg["total_response_time"] += metrics["response_time"]
            current_agg["total_request_size"] += metrics["request_size"]
            current_agg["total_response_size"] += metrics["response_size"]
            
            # Update averages
            total_requests = current_agg["total_requests"]
            current_agg["avg_response_time"] = current_agg["total_response_time"] / total_requests
            current_agg["avg_request_size"] = current_agg["total_request_size"] / total_requests
            current_agg["avg_response_size"] = current_agg["total_response_size"] / total_requests
            
            # Update min/max response times
            response_time = metrics["response_time"]
            current_agg["max_response_time"] = max(current_agg["max_response_time"], response_time)
            current_agg["min_response_time"] = min(current_agg["min_response_time"], response_time)
            
            # Update error count
            if metrics["status_code"] >= 400:
                current_agg["error_count"] += 1
            
            # Update endpoint-specific metrics
            endpoint = metrics["endpoint"]
            if endpoint not in current_agg["endpoints"]:
                current_agg["endpoints"][endpoint] = {
                    "count": 0,
                    "total_time": 0,
                    "avg_time": 0,
                    "errors": 0
                }
            
            endpoint_metrics = current_agg["endpoints"][endpoint]
            endpoint_metrics["count"] += 1
            endpoint_metrics["total_time"] += response_time
            endpoint_metrics["avg_time"] = endpoint_metrics["total_time"] / endpoint_metrics["count"]
            
            if metrics["status_code"] >= 400:
                endpoint_metrics["errors"] += 1
            
            # Store updated aggregated metrics
            cache_service.set(agg_key, current_agg, ttl=86400)  # Store for 24 hours
            
        except Exception as e:
            logger.error(f"Error updating aggregated metrics: {e}")
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with performance monitoring"""
        
        # Record start time and initial metrics
        start_time = time.time()
        start_memory = self._get_memory_usage()
        start_cpu = self._get_cpu_usage()
        
        # Calculate request size
        request_size = self._get_request_size(request)
        
        # Process request
        response = await call_next(request)
        
        # Record end time and final metrics
        end_time = time.time()
        end_memory = self._get_memory_usage()
        end_cpu = self._get_cpu_usage()
        
        # Calculate metrics
        response_time = end_time - start_time
        response_size = self._get_response_size(response)
        memory_delta = end_memory["rss"] - start_memory["rss"]
        cpu_delta = end_cpu - start_cpu
        
        # Prepare metrics data
        metrics = {
            "timestamp": int(start_time),
            "endpoint": f"{request.method} {request.url.path}",
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "response_time": round(response_time * 1000, 2),  # Convert to milliseconds
            "request_size": request_size,
            "response_size": response_size,
            "memory_usage": end_memory,
            "memory_delta": memory_delta,
            "cpu_usage": end_cpu,
            "cpu_delta": cpu_delta,
            "user_agent": request.headers.get("user-agent", ""),
            "client_ip": request.client.host if request.client else None
        }
        
        # Store metrics asynchronously
        self._store_metrics(metrics)
        
        # Add performance headers to response
        response.headers["X-Response-Time"] = f"{response_time:.4f}s"
        response.headers["X-Request-Size"] = str(request_size)
        response.headers["X-Response-Size"] = str(response_size)
        response.headers["X-Memory-Usage"] = f"{end_memory['percent']:.1f}%"
        
        # Log slow requests
        if response_time > 1.0:  # Log requests taking more than 1 second
            logger.warning(
                f"Slow request detected: {request.method} {request.url.path} "
                f"took {response_time:.2f}s (Status: {response.status_code})"
            )
        
        # Log large responses
        if response_size > 1024 * 1024:  # Log responses larger than 1MB
            logger.warning(
                f"Large response detected: {request.method} {request.url.path} "
                f"response size: {response_size / 1024 / 1024:.2f}MB"
            )
        
        return response


class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """Middleware to limit request size for performance"""
    
    def __init__(self, app, max_request_size: int = 10 * 1024 * 1024):  # 10MB default
        super().__init__(app)
        self.max_request_size = max_request_size
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Check request size limits"""
        
        # Check Content-Length header
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                size = int(content_length)
                if size > self.max_request_size:
                    return Response(
                        content=f"Request too large. Maximum size: {self.max_request_size} bytes",
                        status_code=413,
                        headers={"Content-Type": "text/plain"}
                    )
            except ValueError:
                pass
        
        return await call_next(request)


def get_performance_metrics() -> dict:
    """Get current performance metrics from cache"""
    if not cache_service.is_available():
        return {}
    
    try:
        return cache_service.get("dealverse:metrics:aggregated") or {}
    except Exception as e:
        logger.error(f"Error retrieving performance metrics: {e}")
        return {}


def get_endpoint_metrics(endpoint: str = None) -> dict:
    """Get metrics for a specific endpoint or all endpoints"""
    metrics = get_performance_metrics()
    
    if not metrics:
        return {}
    
    if endpoint:
        return metrics.get("endpoints", {}).get(endpoint, {})
    
    return metrics.get("endpoints", {})


def reset_performance_metrics():
    """Reset all performance metrics"""
    if cache_service.is_available():
        cache_service.delete("dealverse:metrics:aggregated")
        cache_service.delete_pattern("dealverse:metrics:*")
        logger.info("Performance metrics reset")
