#!/usr/bin/env python3
"""
S3 Infrastructure Setup Script for DealVerse OS
Automates the creation of S3 buckets, CloudFront distribution, and security policies
"""

import boto3
import json
import sys
import os
from botocore.exceptions import ClientError
from typing import Dict, Any


class S3InfrastructureSetup:
    """Setup S3 infrastructure for DealVerse OS"""
    
    def __init__(self, aws_access_key: str, aws_secret_key: str, region: str = "us-east-1"):
        self.region = region
        self.backup_region = "us-west-2"
        
        # Initialize AWS clients
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=region
        )
        
        self.cloudfront_client = boto3.client(
            'cloudfront',
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name='us-east-1'  # CloudFront is global but uses us-east-1
        )
        
        self.iam_client = boto3.client(
            'iam',
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=region
        )
    
    def create_primary_bucket(self, bucket_name: str) -> Dict[str, Any]:
        """Create primary S3 bucket with security configurations"""
        try:
            # Create bucket
            if self.region == 'us-east-1':
                self.s3_client.create_bucket(Bucket=bucket_name)
            else:
                self.s3_client.create_bucket(
                    Bucket=bucket_name,
                    CreateBucketConfiguration={'LocationConstraint': self.region}
                )
            
            print(f"✅ Created primary bucket: {bucket_name}")
            
            # Enable versioning
            self.s3_client.put_bucket_versioning(
                Bucket=bucket_name,
                VersioningConfiguration={'Status': 'Enabled'}
            )
            print(f"✅ Enabled versioning on {bucket_name}")
            
            # Configure server-side encryption
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
            
            self.s3_client.put_bucket_encryption(
                Bucket=bucket_name,
                ServerSideEncryptionConfiguration=encryption_config
            )
            print(f"✅ Configured encryption for {bucket_name}")
            
            # Block public access
            self.s3_client.put_public_access_block(
                Bucket=bucket_name,
                PublicAccessBlockConfiguration={
                    'BlockPublicAcls': True,
                    'IgnorePublicAcls': True,
                    'BlockPublicPolicy': True,
                    'RestrictPublicBuckets': True
                }
            )
            print(f"✅ Blocked public access for {bucket_name}")
            
            # Configure lifecycle policy
            lifecycle_config = {
                'Rules': [
                    {
                        'ID': 'DealVerseLifecycle',
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
                            }
                        ]
                    }
                ]
            }
            
            self.s3_client.put_bucket_lifecycle_configuration(
                Bucket=bucket_name,
                LifecycleConfiguration=lifecycle_config
            )
            print(f"✅ Configured lifecycle policy for {bucket_name}")
            
            return {"status": "success", "bucket": bucket_name}
            
        except ClientError as e:
            print(f"❌ Failed to create primary bucket: {e}")
            return {"status": "error", "error": str(e)}
    
    def create_backup_bucket(self, backup_bucket_name: str) -> Dict[str, Any]:
        """Create backup S3 bucket in different region"""
        try:
            # Create backup bucket in different region
            backup_s3_client = boto3.client(
                's3',
                aws_access_key_id=self.s3_client._client_config.__dict__['_user_provided_options']['aws_access_key_id'],
                aws_secret_access_key=self.s3_client._client_config.__dict__['_user_provided_options']['aws_secret_access_key'],
                region_name=self.backup_region
            )
            
            backup_s3_client.create_bucket(
                Bucket=backup_bucket_name,
                CreateBucketConfiguration={'LocationConstraint': self.backup_region}
            )
            print(f"✅ Created backup bucket: {backup_bucket_name} in {self.backup_region}")
            
            # Enable versioning
            backup_s3_client.put_bucket_versioning(
                Bucket=backup_bucket_name,
                VersioningConfiguration={'Status': 'Enabled'}
            )
            
            # Configure backup lifecycle with longer retention
            backup_lifecycle_config = {
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
                        ]
                    }
                ]
            }
            
            backup_s3_client.put_bucket_lifecycle_configuration(
                Bucket=backup_bucket_name,
                LifecycleConfiguration=backup_lifecycle_config
            )
            print(f"✅ Configured backup lifecycle for {backup_bucket_name}")
            
            return {"status": "success", "bucket": backup_bucket_name, "region": self.backup_region}
            
        except ClientError as e:
            print(f"❌ Failed to create backup bucket: {e}")
            return {"status": "error", "error": str(e)}
    
    def create_cloudfront_distribution(self, bucket_name: str) -> Dict[str, Any]:
        """Create CloudFront distribution for the S3 bucket"""
        try:
            # Create Origin Access Control (OAC) for S3
            oac_response = self.cloudfront_client.create_origin_access_control(
                OriginAccessControlConfig={
                    'Name': f'dealverse-oac-{bucket_name}',
                    'Description': f'Origin Access Control for DealVerse bucket {bucket_name}',
                    'OriginAccessControlOriginType': 's3',
                    'SigningBehavior': 'always',
                    'SigningProtocol': 'sigv4'
                }
            )
            
            oac_id = oac_response['OriginAccessControl']['Id']
            print(f"✅ Created Origin Access Control: {oac_id}")
            
            # Create CloudFront distribution
            distribution_config = {
                'CallerReference': f'dealverse-{bucket_name}-{int(time.time())}',
                'Comment': f'DealVerse OS CDN for {bucket_name}',
                'DefaultCacheBehavior': {
                    'TargetOriginId': f'{bucket_name}-origin',
                    'ViewerProtocolPolicy': 'redirect-to-https',
                    'AllowedMethods': {
                        'Quantity': 7,
                        'Items': ['GET', 'HEAD', 'OPTIONS', 'PUT', 'POST', 'PATCH', 'DELETE'],
                        'CachedMethods': {
                            'Quantity': 2,
                            'Items': ['GET', 'HEAD']
                        }
                    },
                    'ForwardedValues': {
                        'QueryString': False,
                        'Cookies': {'Forward': 'none'}
                    },
                    'TrustedSigners': {
                        'Enabled': False,
                        'Quantity': 0
                    },
                    'MinTTL': 0,
                    'DefaultTTL': 86400,
                    'MaxTTL': 31536000
                },
                'Origins': {
                    'Quantity': 1,
                    'Items': [
                        {
                            'Id': f'{bucket_name}-origin',
                            'DomainName': f'{bucket_name}.s3.{self.region}.amazonaws.com',
                            'S3OriginConfig': {
                                'OriginAccessIdentity': ''
                            },
                            'OriginAccessControlId': oac_id
                        }
                    ]
                },
                'Enabled': True,
                'PriceClass': 'PriceClass_100'  # Use only North America and Europe edge locations
            }
            
            response = self.cloudfront_client.create_distribution(
                DistributionConfig=distribution_config
            )
            
            distribution_id = response['Distribution']['Id']
            domain_name = response['Distribution']['DomainName']
            
            print(f"✅ Created CloudFront distribution: {distribution_id}")
            print(f"✅ Distribution domain: {domain_name}")
            
            return {
                "status": "success",
                "distribution_id": distribution_id,
                "domain_name": domain_name,
                "oac_id": oac_id
            }
            
        except ClientError as e:
            print(f"❌ Failed to create CloudFront distribution: {e}")
            return {"status": "error", "error": str(e)}
    
    def create_iam_policy(self, bucket_name: str, backup_bucket_name: str) -> Dict[str, Any]:
        """Create IAM policy for DealVerse S3 access"""
        try:
            policy_document = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Action": [
                            "s3:GetObject",
                            "s3:PutObject",
                            "s3:DeleteObject",
                            "s3:GetObjectVersion",
                            "s3:PutObjectAcl"
                        ],
                        "Resource": [
                            f"arn:aws:s3:::{bucket_name}/*",
                            f"arn:aws:s3:::{backup_bucket_name}/*"
                        ]
                    },
                    {
                        "Effect": "Allow",
                        "Action": [
                            "s3:ListBucket",
                            "s3:GetBucketLocation",
                            "s3:GetBucketVersioning"
                        ],
                        "Resource": [
                            f"arn:aws:s3:::{bucket_name}",
                            f"arn:aws:s3:::{backup_bucket_name}"
                        ]
                    },
                    {
                        "Effect": "Allow",
                        "Action": [
                            "cloudfront:CreateInvalidation",
                            "cloudfront:GetInvalidation",
                            "cloudfront:ListInvalidations"
                        ],
                        "Resource": "*"
                    }
                ]
            }
            
            policy_name = "DealVerseS3Policy"
            
            self.iam_client.create_policy(
                PolicyName=policy_name,
                PolicyDocument=json.dumps(policy_document),
                Description="IAM policy for DealVerse OS S3 and CloudFront access"
            )
            
            print(f"✅ Created IAM policy: {policy_name}")
            
            return {"status": "success", "policy_name": policy_name}
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'EntityAlreadyExists':
                print(f"✅ IAM policy already exists")
                return {"status": "success", "policy_name": "DealVerseS3Policy"}
            else:
                print(f"❌ Failed to create IAM policy: {e}")
                return {"status": "error", "error": str(e)}
    
    def setup_complete_infrastructure(self, bucket_name: str) -> Dict[str, Any]:
        """Setup complete S3 infrastructure"""
        print("🚀 Starting DealVerse OS S3 Infrastructure Setup...")
        
        backup_bucket_name = f"{bucket_name}-backup"
        results = {}
        
        # Create primary bucket
        results['primary_bucket'] = self.create_primary_bucket(bucket_name)
        
        # Create backup bucket
        results['backup_bucket'] = self.create_backup_bucket(backup_bucket_name)
        
        # Create CloudFront distribution
        results['cloudfront'] = self.create_cloudfront_distribution(bucket_name)
        
        # Create IAM policy
        results['iam_policy'] = self.create_iam_policy(bucket_name, backup_bucket_name)
        
        print("\n🎉 S3 Infrastructure Setup Complete!")
        print("\n📋 Configuration Summary:")
        print(f"Primary Bucket: {bucket_name}")
        print(f"Backup Bucket: {backup_bucket_name}")
        
        if results['cloudfront']['status'] == 'success':
            print(f"CloudFront Domain: {results['cloudfront']['domain_name']}")
            print(f"Distribution ID: {results['cloudfront']['distribution_id']}")
        
        print("\n⚠️  Next Steps:")
        print("1. Update your .env file with the bucket names and CloudFront domain")
        print("2. Create an IAM user and attach the DealVerseS3Policy")
        print("3. Generate access keys for the IAM user")
        print("4. Test the configuration with a sample upload")
        
        return results


def main():
    """Main setup function"""
    import time
    
    # Get AWS credentials from environment or prompt
    aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    region = os.getenv('AWS_REGION', 'us-east-1')
    
    if not aws_access_key or not aws_secret_key:
        print("❌ AWS credentials not found in environment variables")
        print("Please set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY")
        sys.exit(1)
    
    # Get bucket name
    bucket_name = input("Enter S3 bucket name for DealVerse OS (e.g., dealverse-documents): ").strip()
    
    if not bucket_name:
        print("❌ Bucket name is required")
        sys.exit(1)
    
    # Setup infrastructure
    setup = S3InfrastructureSetup(aws_access_key, aws_secret_key, region)
    results = setup.setup_complete_infrastructure(bucket_name)
    
    # Save configuration to file
    config_file = "s3_setup_results.json"
    with open(config_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Setup results saved to: {config_file}")


if __name__ == "__main__":
    main()
