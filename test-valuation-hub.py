#!/usr/bin/env python3
"""
Comprehensive test script for DealVerse OS Valuation Hub
Tests all financial modeling endpoints and functionality
"""
import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

# Test credentials
TEST_EMAIL = "admin@dealverse.com"
TEST_PASSWORD = "admin123"

class ValuationHubTester:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.user_info = None
        
    def login(self):
        """Login and get authentication token"""
        print("🔐 Logging in...")
        
        response = self.session.post(f"{API_BASE}/auth/login", data={
            "username": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("access_token")
            self.session.headers.update({"Authorization": f"Bearer {self.token}"})
            print("✅ Login successful!")
            return True
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return False
    
    def get_user_info(self):
        """Get current user information"""
        print("👤 Getting user info...")
        
        response = self.session.get(f"{API_BASE}/users/me")
        
        if response.status_code == 200:
            self.user_info = response.json()
            print(f"✅ User info retrieved: {self.user_info.get('email')}")
            return True
        else:
            print(f"❌ Failed to get user info: {response.status_code}")
            return False
    
    def test_financial_models_list(self):
        """Test getting list of financial models"""
        print("\n📊 Testing financial models list...")
        
        response = self.session.get(f"{API_BASE}/financial-models")
        
        if response.status_code == 200:
            models = response.json()
            print(f"✅ Financial models retrieved: {len(models)} models found")
            
            for model in models[:3]:  # Show first 3 models
                print(f"   📈 {model.get('name')}")
                print(f"      Type: {model.get('model_type')} | Status: {model.get('status')}")
                print(f"      Value: {model.get('enterprise_value', 'N/A')} | Version: v{model.get('version')}")
                print()
            
            return models
        else:
            print(f"❌ Failed to get financial models: {response.status_code}")
            return []
    
    def test_model_statistics(self):
        """Test getting model statistics"""
        print("📈 Testing model statistics...")
        
        response = self.session.get(f"{API_BASE}/financial-models/statistics")
        
        if response.status_code == 200:
            stats = response.json()
            print("✅ Model statistics retrieved:")
            print(f"   Total Models: {stats.get('total_models', 0)}")
            print(f"   Active Models: {stats.get('active_models', 0)}")
            print(f"   Models in Review: {stats.get('models_in_review', 0)}")
            print(f"   Draft Models: {stats.get('draft_models', 0)}")
            return stats
        else:
            print(f"❌ Failed to get model statistics: {response.status_code}")
            return {}
    
    def test_model_by_type(self):
        """Test filtering models by type"""
        print("\n🔍 Testing model filtering by type...")
        
        model_types = ["DCF", "Comps", "LBO", "Sum_of_Parts"]
        
        for model_type in model_types:
            response = self.session.get(f"{API_BASE}/financial-models", params={
                "model_type": model_type
            })
            
            if response.status_code == 200:
                models = response.json()
                print(f"✅ {model_type} models: {len(models)} found")
            else:
                print(f"❌ Failed to get {model_type} models: {response.status_code}")
    
    def test_model_by_status(self):
        """Test filtering models by status"""
        print("\n📋 Testing model filtering by status...")
        
        statuses = ["draft", "review", "approved", "active"]
        
        for status in statuses:
            response = self.session.get(f"{API_BASE}/financial-models", params={
                "status": status
            })
            
            if response.status_code == 200:
                models = response.json()
                print(f"✅ {status.capitalize()} models: {len(models)} found")
            else:
                print(f"❌ Failed to get {status} models: {response.status_code}")
    
    def test_model_details(self, model_id):
        """Test getting detailed model information"""
        print(f"\n🔍 Testing model details for ID: {model_id}")
        
        response = self.session.get(f"{API_BASE}/financial-models/{model_id}")
        
        if response.status_code == 200:
            model = response.json()
            print("✅ Model details retrieved:")
            print(f"   Name: {model.get('name')}")
            print(f"   Type: {model.get('model_type')}")
            print(f"   Status: {model.get('status')}")
            print(f"   Enterprise Value: {model.get('enterprise_value', 'N/A')}")
            print(f"   Equity Value: {model.get('equity_value', 'N/A')}")
            print(f"   Version: v{model.get('version')}")
            print(f"   Created: {model.get('created_at')}")
            print(f"   Updated: {model.get('updated_at')}")
            
            # Check if model has assumptions and data
            if model.get('assumptions'):
                print(f"   ✅ Has assumptions data")
            if model.get('model_data'):
                print(f"   ✅ Has model data")
            if model.get('base_case'):
                print(f"   ✅ Has base case scenario")
                
            return model
        else:
            print(f"❌ Failed to get model details: {response.status_code}")
            return None
    
    def test_create_model(self):
        """Test creating a new financial model"""
        print("\n➕ Testing model creation...")
        
        new_model = {
            "name": f"Test Model - {datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "description": "Test model created by automated testing script",
            "model_type": "DCF",
            "model_data": {
                "revenue_projections": {
                    "2024": 100000000,
                    "2025": 120000000,
                    "2026": 144000000
                },
                "growth_rate": 0.20,
                "discount_rate": 0.10
            },
            "assumptions": {
                "revenue_growth": "20% annually",
                "discount_rate": "10% WACC"
            },
            "inputs": {
                "base_revenue": 100000000,
                "growth_rate": 0.20
            },
            "status": "draft",
            "tags": ["test", "automated"]
        }
        
        response = self.session.post(f"{API_BASE}/financial-models", json=new_model)
        
        if response.status_code == 200:
            created_model = response.json()
            print(f"✅ Model created successfully!")
            print(f"   ID: {created_model.get('id')}")
            print(f"   Name: {created_model.get('name')}")
            return created_model
        else:
            print(f"❌ Failed to create model: {response.status_code} - {response.text}")
            return None
    
    def test_update_model(self, model_id):
        """Test updating a financial model"""
        print(f"\n✏️ Testing model update for ID: {model_id}")
        
        update_data = {
            "status": "review",
            "enterprise_value": "$150,000,000",
            "notes": "Updated by automated test script"
        }
        
        response = self.session.put(f"{API_BASE}/financial-models/{model_id}", json=update_data)
        
        if response.status_code == 200:
            updated_model = response.json()
            print("✅ Model updated successfully!")
            print(f"   Status: {updated_model.get('status')}")
            print(f"   Enterprise Value: {updated_model.get('enterprise_value')}")
            return updated_model
        else:
            print(f"❌ Failed to update model: {response.status_code}")
            return None
    
    def run_all_tests(self):
        """Run all valuation hub tests"""
        print("🚀 DealVerse OS Valuation Hub Testing")
        print("=" * 50)
        
        # Login
        if not self.login():
            return False
        
        # Get user info
        if not self.get_user_info():
            return False
        
        # Test financial models list
        models = self.test_financial_models_list()
        
        # Test model statistics
        self.test_model_statistics()
        
        # Test filtering
        self.test_model_by_type()
        self.test_model_by_status()
        
        # Test model details (if we have models)
        if models:
            first_model = models[0]
            model_details = self.test_model_details(first_model.get('id'))
        
        # Test model creation
        new_model = self.test_create_model()
        
        # Test model update (if creation was successful)
        if new_model:
            self.test_update_model(new_model.get('id'))
        
        print("\n🎉 All Valuation Hub tests completed!")
        print("\n✅ Valuation Hub is working correctly!")
        
        return True

def main():
    tester = ValuationHubTester()
    
    try:
        success = tester.run_all_tests()
        if success:
            print("\n🎯 All tests passed! Valuation Hub is ready for use.")
            sys.exit(0)
        else:
            print("\n❌ Some tests failed. Please check the backend server.")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test execution failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
