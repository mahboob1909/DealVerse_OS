#!/usr/bin/env python3
"""
Test script for OpenRouter integration with DealVerse OS
"""
import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.core.ai_config import get_ai_settings, validate_ai_configuration
from app.services.real_ai_service import RealAIService


async def test_openrouter_connection():
    """Test OpenRouter API connection and basic functionality"""
    
    print("🔧 Testing OpenRouter Integration for DealVerse OS")
    print("=" * 50)
    
    # Check configuration
    print("1. Checking AI Configuration...")
    ai_status = validate_ai_configuration()
    print(f"   Configuration Status: {ai_status}")
    
    if not ai_status.get("openrouter_configured", False):
        print("❌ OpenRouter not configured. Please set OPENROUTER_API_KEY in .env file")
        return False
    
    print("✅ OpenRouter configuration found")
    
    # Initialize AI service
    print("\n2. Initializing AI Service...")
    try:
        ai_service = RealAIService()
        service_status = ai_service.get_service_status()
        print(f"   Service Status: {service_status}")
        
        if not service_status.get("openrouter_available", False):
            print("❌ OpenRouter client not available")
            return False
        
        print("✅ AI Service initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize AI service: {str(e)}")
        return False
    
    # Test basic AI call
    print("\n3. Testing Basic AI Call...")
    try:
        # Create a simple test context
        test_context = {
            "document_content": "This is a test document for DealVerse OS AI integration.",
            "document_type": "test",
            "document_title": "Test Document",
            "analysis_type": "general"
        }
        
        # Test document analysis
        response = await ai_service._call_ai_service("document_analysis", test_context)
        print(f"   AI Response Length: {len(response)} characters")
        print(f"   AI Response Preview: {response[:200]}...")
        
        print("✅ Basic AI call successful")
        return True
        
    except Exception as e:
        print(f"❌ AI call failed: {str(e)}")
        return False


async def test_document_analysis():
    """Test document analysis functionality"""
    
    print("\n4. Testing Document Analysis...")
    try:
        from app.schemas.document_analysis import DocumentAnalysisRequest
        from app.services.integrated_ai_service import IntegratedAIService
        
        # Initialize integrated AI service
        integrated_ai = IntegratedAIService()
        
        # Create test request with valid UUID and analysis type
        import uuid
        test_request = DocumentAnalysisRequest(
            document_id=str(uuid.uuid4()),
            analysis_type="full",
            focus_areas=["financial", "legal", "risk"]
        )
        
        # Mock document info
        document_info = {
            "id": "test-doc-001",
            "filename": "test_contract.pdf",
            "content": "This is a sample contract document for testing AI analysis capabilities.",
            "file_type": "pdf",
            "size": 1024
        }
        
        # Test analysis
        result = await integrated_ai.analyze_document(test_request, document_info)
        
        print(f"   Analysis Result: {result.analysis_summary[:100]}...")
        print(f"   Entities Found: {len(result.entities)}")
        print(f"   Risk Score: {result.overall_risk_score}")
        
        print("✅ Document analysis test successful")
        return True
        
    except Exception as e:
        print(f"❌ Document analysis test failed: {str(e)}")
        return False


def main():
    """Main test function"""
    
    # Check if OpenRouter API key is set
    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    if not openrouter_key or openrouter_key == "your-openrouter-api-key":
        print("❌ Please set your actual OpenRouter API key in the .env file")
        print("   Get your API key from: https://openrouter.ai/settings/keys")
        return
    
    # Run tests
    async def run_tests():
        success = True
        
        # Test basic connection
        if not await test_openrouter_connection():
            success = False
        
        # Test document analysis
        if not await test_document_analysis():
            success = False
        
        print("\n" + "=" * 50)
        if success:
            print("🎉 All tests passed! OpenRouter integration is working correctly.")
            print("   You can now use DeepSeek model for AI-powered document analysis.")
        else:
            print("❌ Some tests failed. Please check the configuration and try again.")
    
    # Run the async tests
    asyncio.run(run_tests())


if __name__ == "__main__":
    main()
