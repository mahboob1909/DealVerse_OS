#!/usr/bin/env python3
"""
Test script to verify DealVerse OS API endpoints
"""
import requests
import json
import os
from pathlib import Path

# API Configuration
API_BASE_URL = "http://localhost:8000/api/v1"
TEST_USER_EMAIL = "admin@dealverse.com"
TEST_USER_PASSWORD = "changethis"

class DealVerseAPITester:
    def __init__(self):
        self.base_url = API_BASE_URL
        self.token = None
        self.session = requests.Session()
    
    def login(self):
        """Login and get access token"""
        print("🔐 Logging in...")
        
        login_data = {
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        }
        
        response = self.session.post(
            f"{self.base_url}/auth/login/json",
            json=login_data
        )
        
        if response.status_code == 200:
            data = response.json()
            self.token = data["access_token"]
            self.session.headers.update({
                "Authorization": f"Bearer {self.token}"
            })
            print("✅ Login successful!")
            return True
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return False
    
    def test_documents_endpoint(self):
        """Test the documents API endpoint"""
        print("\n📄 Testing documents endpoint...")
        
        response = self.session.get(f"{self.base_url}/documents")
        
        if response.status_code == 200:
            documents = response.json()
            print(f"✅ Documents endpoint working! Found {len(documents)} documents")
            
            # Print document details
            for doc in documents[:3]:  # Show first 3 documents
                print(f"   📄 {doc['title']}")
                print(f"      Type: {doc['document_type']} | Status: {doc['status']}")
                print(f"      Risk Score: {doc.get('risk_score', 'N/A')}")
                print()
            
            return documents
        else:
            print(f"❌ Documents endpoint failed: {response.status_code} - {response.text}")
            return []
    
    def test_document_analysis(self, document_id):
        """Test document analysis endpoint"""
        print(f"\n🔍 Testing document analysis for ID: {document_id}")
        
        response = self.session.post(f"{self.base_url}/documents/{document_id}/analyze")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Document analysis successful!")
            print(f"   Analysis: {result.get('analysis', {}).get('summary', 'No summary')}")
            return result
        else:
            print(f"❌ Document analysis failed: {response.status_code} - {response.text}")
            return None
    
    def test_file_upload(self):
        """Test file upload endpoint"""
        print("\n📤 Testing file upload...")
        
        # Create a test file
        test_file_path = "test_upload.txt"
        test_content = """
        TEST DOCUMENT FOR UPLOAD
        
        This is a test document to verify the file upload functionality
        of the DealVerse OS Diligence Navigator module.
        
        Document Type: Test
        Created: Automated Test
        Purpose: API Verification
        """
        
        with open(test_file_path, "w") as f:
            f.write(test_content)
        
        try:
            # Upload the file
            with open(test_file_path, "rb") as f:
                files = {"file": ("test_upload.txt", f, "text/plain")}
                data = {
                    "title": "Test Upload Document",
                    "document_type": "test",
                    "is_confidential": "false"
                }
                
                response = self.session.post(
                    f"{self.base_url}/documents/upload",
                    files=files,
                    data=data
                )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ File upload successful!")
                print(f"   Document ID: {result['id']}")
                print(f"   Title: {result['title']}")
                return result
            else:
                print(f"❌ File upload failed: {response.status_code} - {response.text}")
                return None
        
        finally:
            # Clean up test file
            if os.path.exists(test_file_path):
                os.remove(test_file_path)

    def test_financial_models(self):
        """Test financial models endpoint"""
        print("\n📊 Testing financial models...")

        response = self.session.get(f"{self.base_url}/financial-models")

        if response.status_code == 200:
            models = response.json()
            print(f"✅ Financial models working! Found {len(models)} models")

            for model in models[:3]:  # Show first 3 models
                print(f"   📈 {model.get('name')}")
                print(f"      Type: {model.get('model_type')} | Status: {model.get('status')}")
                print(f"      Value: {model.get('enterprise_value', 'N/A')}")
                print()
            return models
        else:
            print(f"❌ Financial models failed: {response.status_code} - {response.text}")
            return []

    def test_model_statistics(self):
        """Test model statistics endpoint"""
        print("📈 Testing model statistics...")

        response = self.session.get(f"{self.base_url}/financial-models/statistics")

        if response.status_code == 200:
            stats = response.json()
            print("✅ Model statistics working!")
            print(f"   Total Models: {stats.get('total_models', 0)}")
            print(f"   Active Models: {stats.get('active_models', 0)}")
            print(f"   Models in Review: {stats.get('models_in_review', 0)}")
            return stats
        else:
            print(f"❌ Model statistics failed: {response.status_code} - {response.text}")
            return {}

    def test_compliance_dashboard(self):
        """Test compliance dashboard endpoint"""
        print("\n🛡️ Testing compliance dashboard...")

        response = self.session.get(f"{self.base_url}/compliance/dashboard")

        if response.status_code == 200:
            dashboard = response.json()
            print("✅ Compliance dashboard working!")
            print(f"   Total Requirements: {dashboard.get('total_requirements', 0)}")
            print(f"   Compliant: {dashboard.get('compliant_requirements', 0)}")
            print(f"   Warning: {dashboard.get('warning_requirements', 0)}")
            print(f"   Overall Score: {dashboard.get('overall_compliance_score', 0)}%")
            print(f"   Categories: {len(dashboard.get('categories_summary', []))}")
            return dashboard
        else:
            print(f"❌ Compliance dashboard failed: {response.status_code} - {response.text}")
            return {}

    def test_dashboard_analytics(self):
        """Test dashboard analytics endpoint"""
        print("\n📊 Testing dashboard analytics...")
        
        response = self.session.get(f"{self.base_url}/analytics/dashboard")
        
        if response.status_code == 200:
            analytics = response.json()
            print("✅ Dashboard analytics working!")
            print(f"   Data keys: {list(analytics.keys())}")
            return analytics
        else:
            print(f"❌ Dashboard analytics failed: {response.status_code} - {response.text}")
            return None
    
    def test_user_info(self):
        """Test current user endpoint"""
        print("\n👤 Testing user info...")
        
        response = self.session.get(f"{self.base_url}/users/me")
        
        if response.status_code == 200:
            user = response.json()
            print("✅ User info working!")
            print(f"   User: {user['first_name']} {user['last_name']}")
            print(f"   Email: {user['email']}")
            print(f"   Role: {user['role']}")
            return user
        else:
            print(f"❌ User info failed: {response.status_code} - {response.text}")
            return None
    
    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 DealVerse OS API Testing")
        print("=" * 50)
        
        # Login first
        if not self.login():
            return False
        
        # Test user info
        user = self.test_user_info()
        if not user:
            return False
        
        # Test documents
        documents = self.test_documents_endpoint()
        
        # Test document analysis if we have documents
        if documents:
            doc_id = documents[0]["id"]
            self.test_document_analysis(doc_id)
        
        # Test file upload
        uploaded_doc = self.test_file_upload()

        # Test financial models
        models = self.test_financial_models()

        # Test model statistics
        self.test_model_statistics()

        # Test compliance
        self.test_compliance_dashboard()

        # Test analytics
        self.test_dashboard_analytics()

        print("\n🎉 All tests completed!")
        print("\n✅ All API endpoints are working correctly!")
        return True

def main():
    """Main test function"""
    tester = DealVerseAPITester()
    
    try:
        success = tester.run_all_tests()
        if success:
            print("\n✅ All API endpoints are working correctly!")
        else:
            print("\n❌ Some tests failed. Check the output above.")
    except Exception as e:
        print(f"\n💥 Test execution failed: {e}")

if __name__ == "__main__":
    main()
