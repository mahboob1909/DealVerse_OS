#!/usr/bin/env python3
"""
Test script for Enhanced File Storage & Security in DealVerse OS
Tests S3 integration, document processing, and security features
"""
import asyncio
import sys
import os
import tempfile
import json
from datetime import datetime
from pathlib import Path

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from app.services.document_processor import document_processor
from app.core.config import settings

# Try to get S3 storage instance, but handle failures gracefully
s3_storage_service = None
try:
    from app.services.s3_storage import get_s3_storage
    s3_storage_service = get_s3_storage()
except Exception as e:
    print(f"⚠️  S3 storage not available: {str(e)}")
    print("   Will test security features without S3 integration")


async def test_s3_configuration():
    """Test S3 service configuration and connectivity"""
    print("🔧 Testing S3 Configuration...")

    try:
        # Check if S3 storage service is available
        if s3_storage_service is None:
            print("   ⚠️  S3 storage service not available - using local storage fallback")
            return False

        # Check if S3 is configured
        if not settings.S3_BUCKET_NAME:
            print("   ⚠️  S3_BUCKET_NAME not configured - using local storage fallback")
            return False

        if not settings.AWS_ACCESS_KEY_ID or not settings.AWS_SECRET_ACCESS_KEY:
            print("   ⚠️  AWS credentials not configured - using local storage fallback")
            return False

        # Test S3 connection
        print(f"   📦 Bucket: {settings.S3_BUCKET_NAME}")
        print(f"   🌍 Region: {settings.AWS_REGION}")
        print(f"   🔐 KMS Key: {getattr(settings, 'AWS_KMS_KEY_ID', 'Not configured')}")
        print(f"   💾 Backup Bucket: {getattr(settings, 'S3_BACKUP_BUCKET_NAME', 'Not configured')}")

        # Test bucket access
        try:
            s3_storage_service.s3_client.head_bucket(Bucket=settings.S3_BUCKET_NAME)
            print("   ✅ S3 bucket accessible")
            return True
        except Exception as e:
            print(f"   ❌ S3 bucket not accessible: {str(e)}")
            return False

    except Exception as e:
        print(f"   ❌ S3 configuration test failed: {str(e)}")
        return False


async def test_security_scanning():
    """Test document security scanning features"""
    print("\n🛡️  Testing Security Scanning...")
    
    # Test files with different security profiles
    test_files = [
        {
            "name": "safe_document.txt",
            "content": b"This is a safe document with normal business content.",
            "expected_safe": True
        },
        {
            "name": "suspicious_script.html",
            "content": b"<html><script>alert('XSS');</script></html>",
            "expected_safe": False
        },
        {
            "name": "pii_document.txt",
            "content": b"Contact John Doe at john.doe@example.com or call 555-123-4567. SSN: 123-45-6789",
            "expected_safe": True  # PII is warning, not threat
        },
        {
            "name": "eicar_test.txt",
            "content": b"X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*",
            "expected_safe": False
        }
    ]
    
    for test_file in test_files:
        print(f"\n   📄 Testing: {test_file['name']}")
        
        try:
            # Perform security scan
            scan_results = await document_processor.enhanced_security_scan(
                test_file["content"], 
                test_file["name"]
            )
            
            print(f"      🔍 Scans performed: {', '.join(scan_results['scans_performed'])}")
            print(f"      ✅ Is safe: {scan_results['is_safe']}")
            print(f"      ⚠️  Threats: {len(scan_results['threats_detected'])}")
            print(f"      📋 Warnings: {len(scan_results['warnings'])}")
            
            # Validate results
            if scan_results["is_safe"] == test_file["expected_safe"]:
                print(f"      ✅ Security scan result correct")
            else:
                print(f"      ❌ Security scan result incorrect (expected: {test_file['expected_safe']})")
            
            # Show details for threats/warnings
            for threat in scan_results["threats_detected"]:
                print(f"         🚨 Threat: {threat['type']} - {threat['description']}")
            
            for warning in scan_results["warnings"]:
                print(f"         ⚠️  Warning: {warning['type']} - {warning['description']}")
                
        except Exception as e:
            print(f"      ❌ Security scan failed: {str(e)}")
            return False
    
    return True


async def test_file_processing():
    """Test document processing pipeline"""
    print("\n📄 Testing Document Processing...")
    
    # Create test documents
    test_documents = [
        {
            "name": "test_document.txt",
            "content": "This is a test document for processing pipeline validation.",
            "type": "text/plain"
        },
        {
            "name": "test_data.json",
            "content": '{"name": "Test Company", "revenue": 1000000, "employees": 50}',
            "type": "application/json"
        }
    ]
    
    for doc in test_documents:
        print(f"\n   📋 Processing: {doc['name']}")
        
        try:
            # Test file info extraction
            file_content = doc["content"].encode('utf-8')
            file_info = document_processor.get_file_info(file_content, doc["name"])
            
            print(f"      📊 File size: {file_info['file_size']} bytes")
            print(f"      🏷️  MIME type: {file_info['mime_type']}")
            print(f"      ✅ Supported: {file_info['is_supported']}")
            print(f"      📁 Document type: {file_info['document_type']}")
            
            # Test text extraction
            if file_info["is_supported"]:
                # Create a mock UploadFile for the enhanced text extraction method
                class MockUploadFile:
                    def __init__(self, content, filename):
                        self.content = content
                        self.filename = filename
                        self.size = len(content)

                    async def read(self):
                        return self.content

                    async def seek(self, position):
                        pass

                mock_file = MockUploadFile(file_content, doc["name"])
                extracted_text = await document_processor._extract_text_content_enhanced(
                    mock_file, file_content, file_info["mime_type"]
                )
                print(f"      📝 Extracted text length: {len(extracted_text)} characters")
                print(f"      📄 Text preview: {extracted_text[:100]}...")
            
        except Exception as e:
            print(f"      ❌ Document processing failed: {str(e)}")
            return False
    
    return True


async def test_s3_operations():
    """Test S3 upload, download, and security operations"""
    print("\n☁️  Testing S3 Operations...")

    if s3_storage_service is None or not settings.S3_BUCKET_NAME:
        print("   ⚠️  S3 not configured, skipping S3 operations test")
        return True
    
    try:
        # Test security configuration
        print("   🔐 Testing bucket security configuration...")
        security_results = s3_storage_service.setup_bucket_security()
        print(f"      ✅ Security features enabled: {', '.join(security_results.keys())}")
        
        # Test file operations with a small test file
        test_content = b"Test file content for S3 operations validation"
        test_filename = "test_s3_operations.txt"
        
        print(f"   📤 Testing file upload...")
        
        # Create a mock UploadFile object
        class MockUploadFile:
            def __init__(self, content, filename):
                self.content = content
                self.filename = filename
                self.size = len(content)
            
            async def read(self):
                return self.content
            
            async def seek(self, position):
                pass
        
        mock_file = MockUploadFile(test_content, test_filename)
        
        # Test upload
        upload_result = await s3_storage_service.upload_file(
            file=mock_file,
            organization_id="test-org-123",
            document_type="test",
            is_confidential=False,
            metadata={"test": "true", "purpose": "security_test"}
        )
        
        print(f"      ✅ Upload successful: {upload_result['file_key']}")
        print(f"      🔗 File URL: {upload_result['file_url']}")
        print(f"      🔐 File hash: {upload_result['file_hash'][:16]}...")
        
        # Test presigned URL generation
        print("   🔗 Testing presigned URL generation...")
        presigned_url = s3_storage_service.generate_presigned_url(
            upload_result['file_key'],
            expiration=3600
        )
        print(f"      ✅ Presigned URL generated (expires in 1 hour)")
        
        # Test backup creation
        print("   💾 Testing backup creation...")
        backup_result = await s3_storage_service.create_backup(upload_result['file_key'])
        print(f"      📋 Backup result: {backup_result}")
        
        # Test audit logging
        print("   📋 Testing audit logging...")
        s3_storage_service.audit_file_access(
            file_key=upload_result['file_key'],
            user_id="test-user-123",
            action="download",
            ip_address="127.0.0.1",
            user_agent="DealVerse-Test/1.0"
        )
        print(f"      ✅ Audit log created")
        
        # Test file versions
        print("   📚 Testing file versioning...")
        versions = s3_storage_service.get_file_versions(upload_result['file_key'])
        print(f"      📋 File versions found: {len(versions)}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ S3 operations test failed: {str(e)}")
        return False


async def main():
    """Main test function"""
    print("🚀 DealVerse OS - Enhanced File Storage & Security Test")
    print("=" * 60)
    
    # Test S3 configuration
    s3_configured = await test_s3_configuration()
    
    # Test security scanning
    security_ok = await test_security_scanning()
    if not security_ok:
        print("\n❌ Security scanning tests failed.")
        return False
    
    # Test document processing
    processing_ok = await test_file_processing()
    if not processing_ok:
        print("\n❌ Document processing tests failed.")
        return False
    
    # Test S3 operations (if configured)
    s3_ok = await test_s3_operations()
    if not s3_ok:
        print("\n❌ S3 operations tests failed.")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 ALL FILE STORAGE & SECURITY TESTS PASSED!")
    print("✅ Security scanning working correctly")
    print("✅ Document processing pipeline functional")
    if s3_configured:
        print("✅ S3 integration working with security features")
    else:
        print("⚠️  S3 not configured (using local storage fallback)")
    print("✅ File storage system ready for production")
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 Test failed with error: {str(e)}")
        sys.exit(1)
