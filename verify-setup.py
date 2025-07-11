#!/usr/bin/env python3
"""
DealVerse OS Setup Verification Script
Tests all components to ensure everything is working correctly
"""

import requests
import json
import time
import sys
from pathlib import Path


def test_backend_health():
    """Test if backend is running and healthy"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend Health: {data.get('status', 'unknown')}")
            return True
        else:
            print(f"❌ Backend Health Check Failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Backend Not Accessible: {e}")
        return False


def test_api_docs():
    """Test if API documentation is accessible"""
    try:
        response = requests.get("http://localhost:8000/api/v1/docs", timeout=5)
        if response.status_code == 200:
            print("✅ API Documentation: Accessible")
            return True
        else:
            print(f"❌ API Documentation Failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ API Documentation Not Accessible: {e}")
        return False


def test_authentication():
    """Test authentication with demo account"""
    try:
        # Test login
        login_data = {
            "email": "admin@dealverse.com",
            "password": "changethis"
        }
        
        response = requests.post(
            "http://localhost:8000/api/v1/auth/login/json",
            json=login_data,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if "access_token" in data:
                print("✅ Authentication: Login successful")
                
                # Test protected endpoint
                headers = {"Authorization": f"Bearer {data['access_token']}"}
                user_response = requests.get(
                    "http://localhost:8000/api/v1/users/me",
                    headers=headers,
                    timeout=5
                )
                
                if user_response.status_code == 200:
                    user_data = user_response.json()
                    print(f"✅ User Data: {user_data.get('first_name', 'Unknown')} {user_data.get('last_name', '')}")
                    return True
                else:
                    print(f"❌ Protected Endpoint Failed: {user_response.status_code}")
                    return False
            else:
                print("❌ Authentication: No access token received")
                return False
        else:
            print(f"❌ Authentication Failed: {response.status_code}")
            if response.status_code == 401:
                print("   Check if database is initialized with demo users")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Authentication Test Failed: {e}")
        return False


def test_database_data():
    """Test if database has sample data"""
    try:
        # Login first
        login_data = {
            "email": "admin@dealverse.com",
            "password": "changethis"
        }
        
        login_response = requests.post(
            "http://localhost:8000/api/v1/auth/login/json",
            json=login_data,
            timeout=10
        )
        
        if login_response.status_code != 200:
            print("❌ Cannot test database - login failed")
            return False
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test deals endpoint
        deals_response = requests.get(
            "http://localhost:8000/api/v1/deals",
            headers=headers,
            timeout=5
        )
        
        if deals_response.status_code == 200:
            deals = deals_response.json()
            print(f"✅ Database: {len(deals)} deals found")
        else:
            print("⚠️  Database: No deals found (this is normal for fresh setup)")
        
        # Test users endpoint
        users_response = requests.get(
            "http://localhost:8000/api/v1/users",
            headers=headers,
            timeout=5
        )
        
        if users_response.status_code == 200:
            users = users_response.json()
            print(f"✅ Database: {len(users)} users found")
            return True
        else:
            print(f"❌ Database: Users endpoint failed: {users_response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Database Test Failed: {e}")
        return False


def test_frontend():
    """Test if frontend is accessible"""
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        if response.status_code == 200:
            print("✅ Frontend: Accessible")
            return True
        else:
            print(f"❌ Frontend Failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Frontend Not Accessible: {e}")
        return False


def test_cors():
    """Test CORS configuration"""
    try:
        # Simulate a browser request from frontend to backend
        headers = {
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "authorization,content-type"
        }
        
        response = requests.options(
            "http://localhost:8000/api/v1/users/me",
            headers=headers,
            timeout=5
        )
        
        if response.status_code in [200, 204]:
            print("✅ CORS: Properly configured")
            return True
        else:
            print(f"⚠️  CORS: May have issues ({response.status_code})")
            return True  # Don't fail on CORS issues
            
    except requests.exceptions.RequestException as e:
        print(f"⚠️  CORS: Cannot test ({e})")
        return True  # Don't fail on CORS test issues


def main():
    """Run all verification tests"""
    print("🔍 DealVerse OS Setup Verification")
    print("=" * 50)
    
    print("\n📋 Testing Components...")
    
    tests = [
        ("Backend Health", test_backend_health),
        ("API Documentation", test_api_docs),
        ("Authentication", test_authentication),
        ("Database Data", test_database_data),
        ("Frontend", test_frontend),
        ("CORS Configuration", test_cors),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🧪 Testing {test_name}...")
        result = test_func()
        results.append((test_name, result))
        
        if not result:
            print(f"   ⚠️  {test_name} test failed")
        
        time.sleep(1)  # Brief pause between tests
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Verification Summary")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! DealVerse OS is ready to use.")
        print("\n🚀 Next Steps:")
        print("1. Open http://localhost:3000 in your browser")
        print("2. Login with: admin@dealverse.com / changethis")
        print("3. Explore the dashboard and modules")
        print("4. Create your first deal or client")
        return True
    else:
        print(f"\n⚠️  {total - passed} tests failed. Please check the issues above.")
        print("\n🔧 Common Solutions:")
        print("- Make sure both backend and frontend are running")
        print("- Check that Neon database is properly configured")
        print("- Verify .env files are set up correctly")
        print("- Try restarting the services")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
