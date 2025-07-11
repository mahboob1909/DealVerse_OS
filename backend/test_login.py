#!/usr/bin/env python3
"""
Test script to verify login functionality
"""
import requests
import json

def test_login():
    """Test the login endpoint"""
    url = "http://localhost:8000/api/v1/auth/login/json"
    
    # Test data
    login_data = {
        "email": "admin@dealverse.com",
        "password": "changethis"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print("Testing login endpoint...")
        print(f"URL: {url}")
        print(f"Data: {login_data}")
        
        response = requests.post(url, json=login_data, headers=headers)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 200:
            print("✅ Login successful!")
            data = response.json()
            print(f"Access Token: {data.get('access_token', 'Not found')[:50]}...")
        else:
            print("❌ Login failed!")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_options():
    """Test the OPTIONS request (CORS preflight)"""
    url = "http://localhost:8000/api/v1/auth/login/json"
    
    headers = {
        "Origin": "http://localhost:3000",
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "Content-Type"
    }
    
    try:
        print("\nTesting OPTIONS request (CORS preflight)...")
        print(f"URL: {url}")
        print(f"Headers: {headers}")
        
        response = requests.options(url, headers=headers)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 200:
            print("✅ OPTIONS request successful!")
        else:
            print("❌ OPTIONS request failed!")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_options()
    test_login()
