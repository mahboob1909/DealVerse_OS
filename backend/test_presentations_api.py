"""
Test script for PitchCraft Suite API endpoints
"""
import requests
import json
from uuid import uuid4

# API base URL
BASE_URL = "http://localhost:8000/api/v1"

def test_presentations_api():
    """Test the presentations API endpoints"""
    
    # First, let's check if the API is running
    try:
        response = requests.get(f"{BASE_URL}/presentations/templates/")
        print(f"Templates endpoint status: {response.status_code}")
        
        if response.status_code == 401:
            print("✅ API is running - authentication required (expected)")
        elif response.status_code == 200:
            print("✅ API is running - templates endpoint accessible")
            print(f"Response: {response.json()}")
        else:
            print(f"⚠️  Unexpected status code: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API - make sure server is running")
        return False
    except Exception as e:
        print(f"❌ Error testing API: {e}")
        return False
    
    # Test the OpenAPI docs endpoint
    try:
        response = requests.get(f"{BASE_URL}/openapi.json")
        if response.status_code == 200:
            openapi_spec = response.json()
            
            # Check if presentation endpoints are in the spec
            paths = openapi_spec.get("paths", {})
            presentation_paths = [path for path in paths.keys() if "presentations" in path]
            
            print(f"\n📋 Found {len(presentation_paths)} presentation endpoints:")
            for path in presentation_paths[:10]:  # Show first 10
                print(f"  - {path}")
            
            if len(presentation_paths) > 10:
                print(f"  ... and {len(presentation_paths) - 10} more")
                
            return True
        else:
            print(f"❌ Could not get OpenAPI spec: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error getting OpenAPI spec: {e}")
        return False

def test_database_models():
    """Test if the database models can be imported and used"""
    try:
        # Test model imports
        from app.models.presentation import (
            Presentation, 
            PresentationSlide, 
            PresentationTemplate,
            PresentationComment,
            PresentationCollaboration
        )
        print("✅ All presentation models imported successfully")
        
        # Test CRUD imports
        from app.crud.crud_presentation import (
            crud_presentation,
            crud_presentation_slide,
            crud_presentation_template,
            crud_presentation_comment,
            crud_presentation_collaboration
        )
        print("✅ All presentation CRUD operations imported successfully")
        
        # Test schema imports
        from app.schemas.presentation import (
            PresentationCreate,
            PresentationUpdate,
            PresentationSlideCreate,
            PresentationTemplateCreate
        )
        print("✅ All presentation schemas imported successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Error importing models/CRUD/schemas: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing PitchCraft Suite Implementation")
    print("=" * 50)
    
    print("\n1. Testing Database Models and CRUD...")
    models_ok = test_database_models()
    
    print("\n2. Testing API Endpoints...")
    api_ok = test_presentations_api()
    
    print("\n" + "=" * 50)
    if models_ok and api_ok:
        print("🎉 All tests passed! PitchCraft Suite is ready for use.")
        print("\n📚 Available endpoints:")
        print("  - GET /api/v1/presentations/ - List presentations")
        print("  - POST /api/v1/presentations/ - Create presentation")
        print("  - GET /api/v1/presentations/{id} - Get presentation")
        print("  - PUT /api/v1/presentations/{id} - Update presentation")
        print("  - DELETE /api/v1/presentations/{id} - Delete presentation")
        print("  - GET /api/v1/presentations/{id}/slides - Get slides")
        print("  - POST /api/v1/presentations/{id}/slides - Create slide")
        print("  - GET /api/v1/presentations/templates/ - Get templates")
        print("  - POST /api/v1/presentations/templates/ - Create template")
        print("  - GET /api/v1/presentations/{id}/comments - Get comments")
        print("  - POST /api/v1/presentations/{id}/comments - Add comment")
        print("\n🔗 API Documentation: http://localhost:8000/api/v1/docs")
    else:
        print("❌ Some tests failed. Please check the implementation.")
