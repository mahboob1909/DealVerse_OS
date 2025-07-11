#!/usr/bin/env python3
"""
Test Backend Connection
Quick test to see if backend is accessible
"""

import requests
import time

def test_backend():
    """Test if backend is running and accessible"""
    print("🔍 Testing Backend Connection")
    print("=" * 40)
    
    backend_urls = [
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://0.0.0.0:8000"
    ]
    
    for url in backend_urls:
        try:
            print(f"🔗 Testing {url}...")
            response = requests.get(f"{url}/health", timeout=5)
            
            if response.status_code == 200:
                print(f"✅ Backend accessible at {url}")
                print(f"📊 Response: {response.json()}")
                return url
            else:
                print(f"❌ Backend returned {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print(f"❌ Cannot connect to {url}")
        except requests.exceptions.Timeout:
            print(f"❌ Timeout connecting to {url}")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n❌ Backend is not accessible")
    return None

def test_login_endpoint(backend_url):
    """Test the login endpoint specifically"""
    print(f"\n🔐 Testing Login Endpoint at {backend_url}")
    print("=" * 40)
    
    try:
        login_url = f"{backend_url}/api/v1/auth/login/json"
        
        # Test with demo credentials
        login_data = {
            "email": "admin@dealverse.com",
            "password": "changethis"
        }
        
        print(f"🔗 POST {login_url}")
        response = requests.post(login_url, json=login_data, timeout=10)
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if "access_token" in data:
                print("✅ Login endpoint working!")
                print("✅ Demo admin account exists")
                return True
            else:
                print("❌ Login response missing access_token")
                print(f"Response: {data}")
        elif response.status_code == 401:
            print("❌ Invalid credentials - database may not be initialized")
        elif response.status_code == 422:
            print("❌ Validation error - check request format")
            print(f"Response: {response.text}")
        else:
            print(f"❌ Unexpected response: {response.text}")
            
    except Exception as e:
        print(f"❌ Login test failed: {e}")
    
    return False

def main():
    """Main test function"""
    # Test basic backend connection
    backend_url = test_backend()
    
    if not backend_url:
        print("\n🔧 Troubleshooting Steps:")
        print("1. Make sure you're in the backend directory")
        print("2. Activate virtual environment: venv\\Scripts\\activate")
        print("3. Start backend: python -m uvicorn app.main:app --reload")
        print("4. Check for error messages in the backend terminal")
        return
    
    # Test login endpoint
    if test_login_endpoint(backend_url):
        print("\n🎉 Backend is working correctly!")
        print("🌐 Frontend should be able to connect now")
        print("🔄 Try refreshing your browser and logging in again")
    else:
        print("\n🔧 Backend is running but login isn't working")
        print("📊 Database may need initialization")
        print("Run: python -c \"import sys; sys.path.append('app'); from app.db.init_db import init_database; init_database()\"")

if __name__ == "__main__":
    main()
