"""
AWS S3 Storage Service for DealVerse OS
Handles secure file upload, download, and management with CloudFront CDN integration
"""

import os
import uuid
import hashlib
import mimetypes
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, BinaryIO
from pathlib import Path
import logging

import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from botocore.config import Config
from fastapi import HTTPException, UploadFile

from app.core.config import settings

logger = logging.getLogger(__name__)


class S3StorageService:
    """AWS S3 storage service with security, CDN, and backup features"""
    
    def __init__(self):
        self.bucket_name = settings.S3_BUCKET_NAME
        self.region = settings.AWS_REGION
        self.cloudfront_domain = getattr(settings, 'CLOUDFRONT_DOMAIN', None)
        self.backup_bucket = getattr(settings, 'S3_BACKUP_BUCKET_NAME', None)
        self.backup_region = getattr(settings, 'AWS_BACKUP_REGION', 'us-west-2')

        # Security configuration
        self.enable_versioning = getattr(settings, 'S3_ENABLE_VERSIONING', True)
        self.enable_lifecycle = getattr(settings, 'S3_ENABLE_LIFECYCLE', True)
        self.enable_access_logging = getattr(settings, 'S3_ENABLE_ACCESS_LOGGING', True)

        # Initialize S3 client with retry configuration
        config = Config(
            region_name=self.region,
            retries={'max_attempts': 3, 'mode': 'adaptive'},
            max_pool_connections=50
        )

        try:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                config=config
            )

            # Initialize backup client if backup bucket is configured
            if self.backup_bucket:
                self.backup_s3_client = boto3.client(
                    's3',
                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                    region_name=self.backup_region,
                    config=config
                )

            # Test connection
            self._test_connection()
            
        except NoCredentialsError:
            logger.error("AWS credentials not found")
            raise HTTPException(status_code=500, detail="AWS credentials not configured")
        except Exception as e:
            logger.error(f"Failed to initialize S3 client: {e}")
            raise HTTPException(status_code=500, detail="Failed to initialize storage service")
    
    def _test_connection(self) -> bool:
        """Test S3 connection and bucket access"""
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            logger.info(f"Successfully connected to S3 bucket: {self.bucket_name}")
            return True
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                logger.error(f"S3 bucket {self.bucket_name} not found")
                raise HTTPException(status_code=500, detail="Storage bucket not found")
            elif error_code == '403':
                logger.error(f"Access denied to S3 bucket {self.bucket_name}")
                raise HTTPException(status_code=500, detail="Storage access denied")
            else:
                logger.error(f"S3 connection error: {e}")
                raise HTTPException(status_code=500, detail="Storage connection failed")
    
    def _generate_file_key(
        self, 
        filename: str, 
        organization_id: str, 
        document_type: str = "general",
        is_confidential: bool = False
    ) -> str:
        """Generate secure S3 object key with organization isolation"""
        # Create unique filename to prevent conflicts
        file_extension = Path(filename).suffix.lower()
        unique_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().strftime("%Y%m%d")
        
        # Organize by confidentiality level
        confidentiality_prefix = "confidential" if is_confidential else "standard"
        
        # Structure: org_id/confidentiality/doc_type/date/unique_id.ext
        key = f"{organization_id}/{confidentiality_prefix}/{document_type}/{timestamp}/{unique_id}{file_extension}"
        
        return key
    
    def _calculate_file_hash(self, file_content: bytes) -> str:
        """Calculate SHA-256 hash of file content for integrity verification"""
        return hashlib.sha256(file_content).hexdigest()
    
    def _get_content_type(self, filename: str) -> str:
        """Determine content type from filename"""
        content_type, _ = mimetypes.guess_type(filename)
        return content_type or 'application/octet-stream'
    
    async def upload_file(
        self,
        file: UploadFile,
        organization_id: str,
        document_type: str = "general",
        is_confidential: bool = False,
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Upload file to S3 with security and metadata
        
        Returns:
            Dict containing file_key, file_url, file_hash, and metadata
        """
        try:
            # Read file content
            file_content = await file.read()
            file_size = len(file_content)
            
            # Validate file size (50MB limit)
            if file_size > 50 * 1024 * 1024:
                raise HTTPException(status_code=400, detail="File too large. Maximum size is 50MB.")
            
            # Generate secure file key
            file_key = self._generate_file_key(
                file.filename, 
                organization_id, 
                document_type, 
                is_confidential
            )
            
            # Calculate file hash for integrity
            file_hash = self._calculate_file_hash(file_content)
            
            # Prepare metadata
            upload_metadata = {
                'original-filename': file.filename,
                'organization-id': organization_id,
                'document-type': document_type,
                'confidential': str(is_confidential).lower(),
                'file-hash': file_hash,
                'upload-timestamp': datetime.utcnow().isoformat(),
                'file-size': str(file_size)
            }
            
            # Add custom metadata if provided
            if metadata:
                upload_metadata.update(metadata)
            
            # Determine content type
            content_type = self._get_content_type(file.filename)
            
            # Configure server-side encryption
            encryption_config = {
                'ServerSideEncryption': 'AES256'
            }
            
            # Add additional security for confidential documents
            if is_confidential:
                encryption_config['ServerSideEncryption'] = 'aws:kms'
                # Use default KMS key or specify custom key
                if hasattr(settings, 'AWS_KMS_KEY_ID') and settings.AWS_KMS_KEY_ID:
                    encryption_config['SSEKMSKeyId'] = settings.AWS_KMS_KEY_ID
            
            # Upload to S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=file_key,
                Body=file_content,
                ContentType=content_type,
                Metadata=upload_metadata,
                **encryption_config
            )
            
            # Generate file URL
            file_url = self._generate_file_url(file_key)
            
            logger.info(f"Successfully uploaded file: {file_key}")
            
            return {
                'file_key': file_key,
                'file_url': file_url,
                'file_hash': file_hash,
                'file_size': file_size,
                'content_type': content_type,
                'metadata': upload_metadata
            }
            
        except ClientError as e:
            logger.error(f"S3 upload error: {e}")
            raise HTTPException(status_code=500, detail="File upload failed")
        except Exception as e:
            logger.error(f"Upload error: {e}")
            raise HTTPException(status_code=500, detail="File upload failed")

    async def upload_file_direct(self, file_content: bytes, file_key: str,
                               content_type: str, metadata: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Upload file content directly to S3 (for processing artifacts)

        Args:
            file_content: Raw file content as bytes
            file_key: S3 object key
            content_type: MIME type of the content
            metadata: Optional metadata dictionary

        Returns:
            Upload result with file information
        """
        try:
            # Prepare metadata
            upload_metadata = {
                "upload_timestamp": datetime.utcnow().isoformat(),
                "content_type": content_type,
                "file_size": str(len(file_content))
            }

            if metadata:
                upload_metadata.update(metadata)

            # Configure encryption
            encryption_config = {'ServerSideEncryption': 'AES256'}

            # Upload to S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=file_key,
                Body=file_content,
                ContentType=content_type,
                Metadata=upload_metadata,
                **encryption_config
            )

            logger.info(f"Direct file upload successful: {file_key}")

            return {
                "file_key": file_key,
                "file_size": len(file_content),
                "content_type": content_type,
                "metadata": upload_metadata,
                "upload_timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"S3 direct file upload failed: {e}")
            raise Exception(f"Direct file upload failed: {e}")

    def download_file_content(self, file_key: str) -> bytes:
        """
        Download file content from S3

        Args:
            file_key: S3 object key

        Returns:
            File content as bytes
        """
        try:
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=file_key
            )

            return response['Body'].read()

        except Exception as e:
            logger.error(f"Failed to download file content: {e}")
            raise Exception(f"S3 download failed: {str(e)}")

    def _generate_file_url(self, file_key: str) -> str:
        """Generate file URL (CloudFront if available, otherwise S3)"""
        if self.cloudfront_domain:
            return f"https://{self.cloudfront_domain}/{file_key}"
        else:
            return f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{file_key}"
    
    def generate_presigned_url(
        self,
        file_key: str,
        expiration: int = 3600,
        operation: str = 'get_object'
    ) -> str:
        """
        Generate presigned URL for secure file access
        
        Args:
            file_key: S3 object key
            expiration: URL expiration time in seconds (default: 1 hour)
            operation: S3 operation ('get_object' or 'put_object')
        """
        try:
            url = self.s3_client.generate_presigned_url(
                operation,
                Params={'Bucket': self.bucket_name, 'Key': file_key},
                ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            logger.error(f"Failed to generate presigned URL: {e}")
            raise HTTPException(status_code=500, detail="Failed to generate secure URL")

    def setup_bucket_security(self) -> Dict[str, Any]:
        """
        Configure advanced security settings for the S3 bucket
        """
        try:
            security_results = {}

            # Enable versioning
            if self.enable_versioning:
                self.s3_client.put_bucket_versioning(
                    Bucket=self.bucket_name,
                    VersioningConfiguration={'Status': 'Enabled'}
                )
                security_results['versioning'] = 'enabled'

            # Configure bucket encryption
            encryption_config = {
                'Rules': [
                    {
                        'ApplyServerSideEncryptionByDefault': {
                            'SSEAlgorithm': 'AES256'
                        },
                        'BucketKeyEnabled': True
                    }
                ]
            }

            # Use KMS encryption if configured
            if hasattr(settings, 'AWS_KMS_KEY_ID') and settings.AWS_KMS_KEY_ID:
                encryption_config['Rules'][0]['ApplyServerSideEncryptionByDefault'] = {
                    'SSEAlgorithm': 'aws:kms',
                    'KMSMasterKeyID': settings.AWS_KMS_KEY_ID
                }

            self.s3_client.put_bucket_encryption(
                Bucket=self.bucket_name,
                ServerSideEncryptionConfiguration=encryption_config
            )
            security_results['encryption'] = 'enabled'

            # Block public access
            self.s3_client.put_public_access_block(
                Bucket=self.bucket_name,
                PublicAccessBlockConfiguration={
                    'BlockPublicAcls': True,
                    'IgnorePublicAcls': True,
                    'BlockPublicPolicy': True,
                    'RestrictPublicBuckets': True
                }
            )
            security_results['public_access_blocked'] = True

            # Configure lifecycle policy
            if self.enable_lifecycle:
                lifecycle_config = {
                    'Rules': [
                        {
                            'ID': 'DealVerseLifecycleRule',
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
                            'NoncurrentVersionTransitions': [
                                {
                                    'NoncurrentDays': 30,
                                    'StorageClass': 'STANDARD_IA'
                                }
                            ],
                            'NoncurrentVersionExpiration': {
                                'NoncurrentDays': 365
                            }
                        }
                    ]
                }

                self.s3_client.put_bucket_lifecycle_configuration(
                    Bucket=self.bucket_name,
                    LifecycleConfiguration=lifecycle_config
                )
                security_results['lifecycle'] = 'enabled'

            # Configure access logging
            if self.enable_access_logging:
                logging_config = {
                    'LoggingEnabled': {
                        'TargetBucket': self.bucket_name,
                        'TargetPrefix': 'access-logs/'
                    }
                }

                self.s3_client.put_bucket_logging(
                    Bucket=self.bucket_name,
                    BucketLoggingStatus=logging_config
                )
                security_results['access_logging'] = 'enabled'

            logger.info(f"S3 bucket security configured: {security_results}")
            return security_results

        except ClientError as e:
            logger.error(f"Failed to configure bucket security: {e}")
            raise HTTPException(status_code=500, detail="Failed to configure bucket security")

    async def create_backup(self, file_key: str) -> Dict[str, Any]:
        """
        Create cross-region backup of important files
        """
        if not self.backup_bucket:
            logger.warning("Backup bucket not configured, skipping backup")
            return {"backup_created": False, "reason": "backup_bucket_not_configured"}

        try:
            # Copy object to backup bucket
            copy_source = {'Bucket': self.bucket_name, 'Key': file_key}

            self.backup_s3_client.copy_object(
                CopySource=copy_source,
                Bucket=self.backup_bucket,
                Key=file_key,
                ServerSideEncryption='AES256',
                MetadataDirective='COPY'
            )

            logger.info(f"Backup created for file: {file_key}")
            return {
                "backup_created": True,
                "backup_bucket": self.backup_bucket,
                "backup_region": self.backup_region,
                "backup_timestamp": datetime.utcnow().isoformat()
            }

        except ClientError as e:
            logger.error(f"Failed to create backup for {file_key}: {e}")
            return {"backup_created": False, "error": str(e)}

    def audit_file_access(self, file_key: str, user_id: str, action: str,
                         ip_address: str = None, user_agent: str = None) -> None:
        """
        Log file access for audit purposes
        """
        audit_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "file_key": file_key,
            "user_id": user_id,
            "action": action,
            "ip_address": ip_address,
            "user_agent": user_agent
        }

        # Store audit log in S3
        audit_key = f"audit-logs/{datetime.utcnow().strftime('%Y/%m/%d')}/{uuid.uuid4()}.json"

        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=audit_key,
                Body=json.dumps(audit_data),
                ContentType='application/json',
                ServerSideEncryption='AES256'
            )

            logger.info(f"Audit log created: {action} on {file_key} by {user_id}")

        except ClientError as e:
            logger.error(f"Failed to create audit log: {e}")

    def get_file_versions(self, file_key: str) -> List[Dict[str, Any]]:
        """
        Get all versions of a file
        """
        try:
            response = self.s3_client.list_object_versions(
                Bucket=self.bucket_name,
                Prefix=file_key
            )

            versions = []
            for version in response.get('Versions', []):
                if version['Key'] == file_key:
                    versions.append({
                        'version_id': version['VersionId'],
                        'last_modified': version['LastModified'].isoformat(),
                        'size': version['Size'],
                        'is_latest': version['IsLatest']
                    })

            return sorted(versions, key=lambda x: x['last_modified'], reverse=True)

        except ClientError as e:
            logger.error(f"Failed to get file versions for {file_key}: {e}")
            return []
    
    async def download_file(self, file_key: str) -> bytes:
        """Download file content from S3"""
        try:
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=file_key)
            return response['Body'].read()
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                raise HTTPException(status_code=404, detail="File not found")
            logger.error(f"S3 download error: {e}")
            raise HTTPException(status_code=500, detail="File download failed")
    
    def get_file_metadata(self, file_key: str) -> Dict[str, Any]:
        """Get file metadata from S3"""
        try:
            response = self.s3_client.head_object(Bucket=self.bucket_name, Key=file_key)
            return {
                'content_type': response.get('ContentType'),
                'content_length': response.get('ContentLength'),
                'last_modified': response.get('LastModified'),
                'etag': response.get('ETag'),
                'metadata': response.get('Metadata', {}),
                'server_side_encryption': response.get('ServerSideEncryption')
            }
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                raise HTTPException(status_code=404, detail="File not found")
            logger.error(f"Failed to get file metadata: {e}")
            raise HTTPException(status_code=500, detail="Failed to get file information")
    
    def delete_file(self, file_key: str) -> bool:
        """Delete file from S3"""
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=file_key)
            logger.info(f"Successfully deleted file: {file_key}")
            return True
        except ClientError as e:
            logger.error(f"Failed to delete file: {e}")
            raise HTTPException(status_code=500, detail="File deletion failed")
    
    def copy_file(self, source_key: str, destination_key: str) -> bool:
        """Copy file within S3 bucket"""
        try:
            copy_source = {'Bucket': self.bucket_name, 'Key': source_key}
            self.s3_client.copy_object(
                CopySource=copy_source,
                Bucket=self.bucket_name,
                Key=destination_key
            )
            logger.info(f"Successfully copied file from {source_key} to {destination_key}")
            return True
        except ClientError as e:
            logger.error(f"Failed to copy file: {e}")
            raise HTTPException(status_code=500, detail="File copy failed")
    
    def list_files(
        self,
        prefix: str = "",
        max_keys: int = 1000
    ) -> List[Dict[str, Any]]:
        """List files in S3 bucket with optional prefix filter"""
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix,
                MaxKeys=max_keys
            )
            
            files = []
            for obj in response.get('Contents', []):
                files.append({
                    'key': obj['Key'],
                    'size': obj['Size'],
                    'last_modified': obj['LastModified'],
                    'etag': obj['ETag']
                })
            
            return files
        except ClientError as e:
            logger.error(f"Failed to list files: {e}")
            raise HTTPException(status_code=500, detail="Failed to list files")


# Global instance - lazy initialization
s3_storage = None

def get_s3_storage():
    """Get S3 storage instance with lazy initialization"""
    global s3_storage
    if s3_storage is None:
        s3_storage = S3StorageService()
    return s3_storage
