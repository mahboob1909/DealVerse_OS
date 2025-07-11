"""
CloudFront CDN Service for DealVerse OS
Handles CDN distribution, cache management, and secure content delivery
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

import boto3
from botocore.exceptions import ClientError
from botocore.config import Config
from fastapi import HTTPException

from app.core.config import settings

logger = logging.getLogger(__name__)


class CDNService:
    """CloudFront CDN service for optimized content delivery"""
    
    def __init__(self):
        self.cloudfront_domain = getattr(settings, 'CLOUDFRONT_DOMAIN', None)
        self.distribution_id = getattr(settings, 'CLOUDFRONT_DISTRIBUTION_ID', None)
        
        # Initialize CloudFront client
        config = Config(
            region_name='us-east-1',  # CloudFront is global but uses us-east-1
            retries={'max_attempts': 3, 'mode': 'adaptive'}
        )
        
        try:
            self.cloudfront_client = boto3.client(
                'cloudfront',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                config=config
            )
        except Exception as e:
            logger.error(f"Failed to initialize CloudFront client: {e}")
            self.cloudfront_client = None
    
    def is_enabled(self) -> bool:
        """Check if CDN is properly configured"""
        return (
            self.cloudfront_client is not None and 
            self.cloudfront_domain is not None and 
            self.distribution_id is not None
        )
    
    def get_cdn_url(self, file_key: str, secure: bool = True) -> str:
        """
        Generate CDN URL for file access
        
        Args:
            file_key: S3 object key
            secure: Use HTTPS (default: True)
        """
        if not self.is_enabled():
            # Fallback to direct S3 URL
            protocol = "https" if secure else "http"
            return f"{protocol}://{settings.S3_BUCKET_NAME}.s3.{settings.AWS_REGION}.amazonaws.com/{file_key}"
        
        protocol = "https" if secure else "http"
        return f"{protocol}://{self.cloudfront_domain}/{file_key}"
    
    def generate_signed_url(
        self,
        file_key: str,
        expiration_hours: int = 24,
        ip_address: Optional[str] = None
    ) -> str:
        """
        Generate signed CloudFront URL for secure access
        
        Args:
            file_key: S3 object key
            expiration_hours: URL expiration time in hours
            ip_address: Optional IP address restriction
        """
        if not self.is_enabled():
            raise HTTPException(status_code=500, detail="CDN not configured")
        
        try:
            # Calculate expiration time
            expire_date = datetime.utcnow() + timedelta(hours=expiration_hours)
            
            # Create CloudFront URL signer (requires private key)
            # This is a simplified version - in production, you'd use boto3's CloudFrontSigner
            base_url = self.get_cdn_url(file_key)
            
            # For now, return the base URL with expiration parameter
            # In production, implement proper CloudFront signing
            return f"{base_url}?expires={int(expire_date.timestamp())}"
            
        except Exception as e:
            logger.error(f"Failed to generate signed URL: {e}")
            raise HTTPException(status_code=500, detail="Failed to generate secure URL")
    
    def invalidate_cache(self, file_keys: List[str]) -> Dict[str, Any]:
        """
        Invalidate CloudFront cache for specific files
        
        Args:
            file_keys: List of S3 object keys to invalidate
        """
        if not self.is_enabled():
            logger.warning("CDN not configured, skipping cache invalidation")
            return {"status": "skipped", "reason": "CDN not configured"}
        
        try:
            # Prepare invalidation paths
            paths = [f"/{key}" for key in file_keys]
            
            # Create invalidation
            response = self.cloudfront_client.create_invalidation(
                DistributionId=self.distribution_id,
                InvalidationBatch={
                    'Paths': {
                        'Quantity': len(paths),
                        'Items': paths
                    },
                    'CallerReference': f"dealverse-{datetime.utcnow().isoformat()}"
                }
            )
            
            invalidation_id = response['Invalidation']['Id']
            logger.info(f"Created CloudFront invalidation: {invalidation_id}")
            
            return {
                "status": "success",
                "invalidation_id": invalidation_id,
                "paths": paths
            }
            
        except ClientError as e:
            logger.error(f"CloudFront invalidation failed: {e}")
            raise HTTPException(status_code=500, detail="Cache invalidation failed")
    
    def get_invalidation_status(self, invalidation_id: str) -> Dict[str, Any]:
        """Get status of CloudFront invalidation"""
        if not self.is_enabled():
            raise HTTPException(status_code=500, detail="CDN not configured")
        
        try:
            response = self.cloudfront_client.get_invalidation(
                DistributionId=self.distribution_id,
                Id=invalidation_id
            )
            
            invalidation = response['Invalidation']
            return {
                "id": invalidation['Id'],
                "status": invalidation['Status'],
                "create_time": invalidation['CreateTime'],
                "paths": invalidation['InvalidationBatch']['Paths']['Items']
            }
            
        except ClientError as e:
            logger.error(f"Failed to get invalidation status: {e}")
            raise HTTPException(status_code=500, detail="Failed to get invalidation status")
    
    def get_distribution_config(self) -> Dict[str, Any]:
        """Get CloudFront distribution configuration"""
        if not self.is_enabled():
            raise HTTPException(status_code=500, detail="CDN not configured")
        
        try:
            response = self.cloudfront_client.get_distribution_config(
                Id=self.distribution_id
            )
            
            config = response['DistributionConfig']
            return {
                "domain_name": config.get('DomainName'),
                "status": config.get('Enabled'),
                "price_class": config.get('PriceClass'),
                "origins": [
                    {
                        "id": origin.get('Id'),
                        "domain_name": origin.get('DomainName'),
                        "origin_path": origin.get('OriginPath', '')
                    }
                    for origin in config.get('Origins', {}).get('Items', [])
                ],
                "default_cache_behavior": {
                    "target_origin_id": config.get('DefaultCacheBehavior', {}).get('TargetOriginId'),
                    "viewer_protocol_policy": config.get('DefaultCacheBehavior', {}).get('ViewerProtocolPolicy'),
                    "allowed_methods": config.get('DefaultCacheBehavior', {}).get('AllowedMethods', {}).get('Items', []),
                    "cached_methods": config.get('DefaultCacheBehavior', {}).get('AllowedMethods', {}).get('CachedMethods', {}).get('Items', [])
                }
            }
            
        except ClientError as e:
            logger.error(f"Failed to get distribution config: {e}")
            raise HTTPException(status_code=500, detail="Failed to get CDN configuration")
    
    def get_cache_statistics(self, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """
        Get CloudFront cache statistics using CloudWatch
        
        Args:
            start_time: Start time for statistics
            end_time: End time for statistics
        """
        if not self.is_enabled():
            raise HTTPException(status_code=500, detail="CDN not configured")
        
        try:
            # Initialize CloudWatch client
            cloudwatch = boto3.client(
                'cloudwatch',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name='us-east-1'
            )
            
            # Get CloudFront metrics
            metrics = [
                'Requests',
                'BytesDownloaded',
                'BytesUploaded',
                '4xxErrorRate',
                '5xxErrorRate',
                'CacheHitRate'
            ]
            
            statistics = {}
            
            for metric in metrics:
                response = cloudwatch.get_metric_statistics(
                    Namespace='AWS/CloudFront',
                    MetricName=metric,
                    Dimensions=[
                        {
                            'Name': 'DistributionId',
                            'Value': self.distribution_id
                        }
                    ],
                    StartTime=start_time,
                    EndTime=end_time,
                    Period=3600,  # 1 hour periods
                    Statistics=['Sum', 'Average']
                )
                
                statistics[metric] = {
                    'datapoints': response['Datapoints'],
                    'label': response['Label']
                }
            
            return statistics
            
        except Exception as e:
            logger.error(f"Failed to get cache statistics: {e}")
            raise HTTPException(status_code=500, detail="Failed to get cache statistics")
    
    def configure_security_headers(self) -> Dict[str, str]:
        """Get recommended security headers for CDN responses"""
        return {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
            'Content-Security-Policy': "default-src 'self'",
            'Referrer-Policy': 'strict-origin-when-cross-origin'
        }
    
    def get_edge_locations(self) -> List[Dict[str, str]]:
        """Get list of CloudFront edge locations"""
        # This would typically come from AWS API or be hardcoded
        # Simplified version for demonstration
        return [
            {"code": "IAD", "city": "Washington DC", "country": "United States"},
            {"code": "DFW", "city": "Dallas", "country": "United States"},
            {"code": "LAX", "city": "Los Angeles", "country": "United States"},
            {"code": "LHR", "city": "London", "country": "United Kingdom"},
            {"code": "FRA", "city": "Frankfurt", "country": "Germany"},
            {"code": "NRT", "city": "Tokyo", "country": "Japan"},
            {"code": "SYD", "city": "Sydney", "country": "Australia"}
        ]


# Global instance
cdn_service = CDNService()
