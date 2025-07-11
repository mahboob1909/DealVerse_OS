"""
Backup and Disaster Recovery Service for DealVerse OS
Handles automated backups, cross-region replication, and disaster recovery
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import json

import boto3
from botocore.exceptions import ClientError
from botocore.config import Config
from fastapi import HTTPException

from app.core.config import settings

logger = logging.getLogger(__name__)


class BackupService:
    """Comprehensive backup and disaster recovery service"""
    
    def __init__(self):
        self.primary_bucket = settings.S3_BUCKET_NAME
        self.backup_bucket = getattr(settings, 'S3_BACKUP_BUCKET_NAME', f"{self.primary_bucket}-backup")
        self.backup_region = getattr(settings, 'AWS_BACKUP_REGION', 'us-west-2')
        self.retention_days = getattr(settings, 'BACKUP_RETENTION_DAYS', 90)
        
        # Initialize S3 clients for primary and backup regions
        config = Config(
            retries={'max_attempts': 3, 'mode': 'adaptive'},
            max_pool_connections=50
        )
        
        try:
            # Primary region client
            self.s3_primary = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION,
                config=config
            )
            
            # Backup region client
            self.s3_backup = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=self.backup_region,
                config=config
            )
            
            # Initialize backup infrastructure
            self._initialize_backup_infrastructure()
            
        except Exception as e:
            logger.error(f"Failed to initialize backup service: {e}")
            raise HTTPException(status_code=500, detail="Backup service initialization failed")
    
    def _initialize_backup_infrastructure(self):
        """Initialize backup buckets and policies"""
        try:
            # Check if backup bucket exists, create if not
            try:
                self.s3_backup.head_bucket(Bucket=self.backup_bucket)
                logger.info(f"Backup bucket {self.backup_bucket} already exists")
            except ClientError as e:
                if e.response['Error']['Code'] == '404':
                    # Create backup bucket
                    if self.backup_region == 'us-east-1':
                        self.s3_backup.create_bucket(Bucket=self.backup_bucket)
                    else:
                        self.s3_backup.create_bucket(
                            Bucket=self.backup_bucket,
                            CreateBucketConfiguration={'LocationConstraint': self.backup_region}
                        )
                    logger.info(f"Created backup bucket: {self.backup_bucket}")
                else:
                    raise
            
            # Configure backup bucket lifecycle policy
            self._configure_backup_lifecycle()
            
            # Enable versioning on backup bucket
            self._enable_backup_versioning()
            
        except Exception as e:
            logger.error(f"Failed to initialize backup infrastructure: {e}")
    
    def _configure_backup_lifecycle(self):
        """Configure lifecycle policy for backup bucket"""
        try:
            lifecycle_config = {
                'Rules': [
                    {
                        'ID': 'DealVerseBackupLifecycle',
                        'Status': 'Enabled',
                        'Filter': {'Prefix': ''},
                        'Transitions': [
                            {
                                'Days': 30,
                                'StorageClass': 'STANDARD_IA'
                            },
                            {
                                'Days': 90,
                                'StorageClass': 'GLACIER'
                            },
                            {
                                'Days': 365,
                                'StorageClass': 'DEEP_ARCHIVE'
                            }
                        ],
                        'Expiration': {
                            'Days': self.retention_days * 365  # Keep for multiple years in deep archive
                        }
                    }
                ]
            }
            
            self.s3_backup.put_bucket_lifecycle_configuration(
                Bucket=self.backup_bucket,
                LifecycleConfiguration=lifecycle_config
            )
            
            logger.info("Configured backup lifecycle policy")
            
        except ClientError as e:
            logger.error(f"Failed to configure backup lifecycle: {e}")
    
    def _enable_backup_versioning(self):
        """Enable versioning on backup bucket"""
        try:
            self.s3_backup.put_bucket_versioning(
                Bucket=self.backup_bucket,
                VersioningConfiguration={'Status': 'Enabled'}
            )
            logger.info("Enabled versioning on backup bucket")
        except ClientError as e:
            logger.error(f"Failed to enable backup versioning: {e}")
    
    def backup_file(self, file_key: str, metadata: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Backup a single file to the backup region
        
        Args:
            file_key: S3 object key to backup
            metadata: Additional metadata for the backup
        """
        try:
            # Generate backup key with timestamp
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            backup_key = f"backups/{timestamp}/{file_key}"
            
            # Copy from primary to backup bucket
            copy_source = {
                'Bucket': self.primary_bucket,
                'Key': file_key
            }
            
            # Prepare backup metadata
            backup_metadata = {
                'backup-timestamp': datetime.utcnow().isoformat(),
                'original-bucket': self.primary_bucket,
                'original-key': file_key,
                'backup-type': 'manual'
            }
            
            if metadata:
                backup_metadata.update(metadata)
            
            # Perform cross-region copy
            self.s3_backup.copy_object(
                CopySource=copy_source,
                Bucket=self.backup_bucket,
                Key=backup_key,
                Metadata=backup_metadata,
                MetadataDirective='REPLACE',
                ServerSideEncryption='AES256'
            )
            
            logger.info(f"Successfully backed up {file_key} to {backup_key}")
            
            return {
                'status': 'success',
                'original_key': file_key,
                'backup_key': backup_key,
                'backup_bucket': self.backup_bucket,
                'backup_region': self.backup_region,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except ClientError as e:
            logger.error(f"Failed to backup file {file_key}: {e}")
            raise HTTPException(status_code=500, detail=f"Backup failed for {file_key}")
    
    def restore_file(self, backup_key: str, restore_key: Optional[str] = None) -> Dict[str, Any]:
        """
        Restore a file from backup
        
        Args:
            backup_key: Backup file key
            restore_key: Optional custom restore key (defaults to original location)
        """
        try:
            # Get backup metadata to determine original location
            backup_metadata = self.s3_backup.head_object(
                Bucket=self.backup_bucket,
                Key=backup_key
            )
            
            original_key = backup_metadata['Metadata'].get('original-key')
            if not restore_key:
                restore_key = original_key
            
            # Copy from backup to primary bucket
            copy_source = {
                'Bucket': self.backup_bucket,
                'Key': backup_key
            }
            
            self.s3_primary.copy_object(
                CopySource=copy_source,
                Bucket=self.primary_bucket,
                Key=restore_key,
                ServerSideEncryption='AES256'
            )
            
            logger.info(f"Successfully restored {backup_key} to {restore_key}")
            
            return {
                'status': 'success',
                'backup_key': backup_key,
                'restored_key': restore_key,
                'original_key': original_key,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except ClientError as e:
            logger.error(f"Failed to restore file {backup_key}: {e}")
            raise HTTPException(status_code=500, detail=f"Restore failed for {backup_key}")
    
    def schedule_automated_backup(self, organization_id: str) -> Dict[str, Any]:
        """
        Schedule automated backup for an organization's files
        
        Args:
            organization_id: Organization ID to backup
        """
        try:
            # List all files for the organization
            prefix = f"{organization_id}/"
            
            response = self.s3_primary.list_objects_v2(
                Bucket=self.primary_bucket,
                Prefix=prefix
            )
            
            backup_results = []
            
            for obj in response.get('Contents', []):
                file_key = obj['Key']
                
                # Skip already backed up files (check if backup exists)
                if not self._is_recently_backed_up(file_key):
                    backup_result = self.backup_file(
                        file_key,
                        metadata={'backup-type': 'automated', 'organization-id': organization_id}
                    )
                    backup_results.append(backup_result)
            
            logger.info(f"Completed automated backup for organization {organization_id}")
            
            return {
                'status': 'success',
                'organization_id': organization_id,
                'files_backed_up': len(backup_results),
                'backup_results': backup_results,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Automated backup failed for organization {organization_id}: {e}")
            raise HTTPException(status_code=500, detail="Automated backup failed")
    
    def _is_recently_backed_up(self, file_key: str, hours: int = 24) -> bool:
        """Check if file has been backed up recently"""
        try:
            # Look for recent backups
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            
            # List recent backups for this file
            prefix = f"backups/{cutoff_time.strftime('%Y%m%d')}"
            
            response = self.s3_backup.list_objects_v2(
                Bucket=self.backup_bucket,
                Prefix=prefix
            )
            
            for obj in response.get('Contents', []):
                if file_key in obj['Key']:
                    return True
            
            return False
            
        except Exception:
            # If we can't check, assume not backed up
            return False
    
    def get_backup_status(self, organization_id: Optional[str] = None) -> Dict[str, Any]:
        """Get backup status and statistics"""
        try:
            prefix = f"backups/"
            if organization_id:
                # This would require more sophisticated organization tracking
                pass
            
            response = self.s3_backup.list_objects_v2(
                Bucket=self.backup_bucket,
                Prefix=prefix
            )
            
            total_backups = len(response.get('Contents', []))
            total_size = sum(obj['Size'] for obj in response.get('Contents', []))
            
            # Get recent backups (last 7 days)
            recent_cutoff = datetime.utcnow() - timedelta(days=7)
            recent_backups = [
                obj for obj in response.get('Contents', [])
                if obj['LastModified'] > recent_cutoff
            ]
            
            return {
                'total_backups': total_backups,
                'total_size_bytes': total_size,
                'total_size_gb': round(total_size / (1024**3), 2),
                'recent_backups': len(recent_backups),
                'backup_bucket': self.backup_bucket,
                'backup_region': self.backup_region,
                'retention_days': self.retention_days,
                'last_updated': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get backup status: {e}")
            raise HTTPException(status_code=500, detail="Failed to get backup status")
    
    def cleanup_old_backups(self, days: Optional[int] = None) -> Dict[str, Any]:
        """Clean up old backups beyond retention period"""
        try:
            cleanup_days = days or self.retention_days
            cutoff_date = datetime.utcnow() - timedelta(days=cleanup_days)
            
            response = self.s3_backup.list_objects_v2(
                Bucket=self.backup_bucket,
                Prefix="backups/"
            )
            
            deleted_count = 0
            deleted_size = 0
            
            for obj in response.get('Contents', []):
                if obj['LastModified'] < cutoff_date:
                    self.s3_backup.delete_object(
                        Bucket=self.backup_bucket,
                        Key=obj['Key']
                    )
                    deleted_count += 1
                    deleted_size += obj['Size']
            
            logger.info(f"Cleaned up {deleted_count} old backups")
            
            return {
                'status': 'success',
                'deleted_count': deleted_count,
                'deleted_size_bytes': deleted_size,
                'deleted_size_gb': round(deleted_size / (1024**3), 2),
                'cutoff_date': cutoff_date.isoformat(),
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to cleanup old backups: {e}")
            raise HTTPException(status_code=500, detail="Backup cleanup failed")


# Global instance
backup_service = BackupService()
