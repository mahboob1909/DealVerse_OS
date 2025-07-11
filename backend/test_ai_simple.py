#!/usr/bin/env python3
"""
Simple AI Integration Test for DealVerse OS
Quick test to verify AI services are working
"""
import asyncio
import sys
import os
import uuid
from datetime import datetime

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from app.core.ai_config import get_ai_settings, validate_ai_configuration
from app.services.integrated_ai_service import integrated_ai_service
from app.services.prospect_ai import prospect_ai_service
from app.services.compliance_ai import compliance_ai_service
from app.schemas.document_analysis import DocumentAnalysisRequest
from app.schemas.prospect import ProspectAnalysisRequest


async def test_ai_status():
    """Test AI service status"""
    print("🔧 Testing AI Service Status...")
    
    # Check configuration
    config = validate_ai_configuration()
    print(f"   AI Configuration: {config}")
    
    # Check service status
    status = integrated_ai_service.get_service_status()
    print(f"   Service Status: {status.get('real_ai_enabled', False)}")
    
    return config.get('openrouter_configured', False) or config.get('openai_configured', False)


async def test_document_analysis_simple():
    """Simple document analysis test"""
    print("\n📄 Testing Document Analysis (Simple)...")
    
    # Simple test document
    doc_content = """
    ACME Corp Financial Summary
    Revenue: $10,000,000
    Profit: $2,000,000
    Risk: Market volatility
    """
    
    request = DocumentAnalysisRequest(
        document_id=str(uuid.uuid4()),
        analysis_type="full",
        priority="medium"
    )
    
    document_info = {
        "id": str(uuid.uuid4()),
        "title": "Simple Test Document",
        "document_type": "financial_statement",
        "content": doc_content,
        "file_size": len(doc_content),
        "file_type": "text"
    }
    
    try:
        result = await integrated_ai_service.analyze_document(request, document_info)
        print(f"   ✅ Analysis Status: {result.status}")
        print(f"   📊 Risk Score: {result.overall_risk_score}")
        print(f"   🎯 Confidence: {result.confidence_score}")
        print(f"   📝 Summary: {result.summary[:100]}...")
        return True
    except Exception as e:
        print(f"   ❌ Analysis failed: {str(e)}")
        return False


async def test_prospect_analysis_simple():
    """Simple prospect analysis test"""
    print("\n🎯 Testing Prospect Analysis (Simple)...")
    
    request = ProspectAnalysisRequest(
        company_name="Test Company Inc",
        industry="Technology",
        revenue=10000000,
        employee_count=100,
        location="New York, NY"
    )
    
    try:
        result = await prospect_ai_service.analyze_prospect(request)
        print(f"   ✅ Analysis completed")
        print(f"   📊 AI Score: {result.ai_score}")
        print(f"   🎯 Confidence: {result.confidence_level}")
        print(f"   💰 Deal Probability: {result.deal_probability}%")
        print(f"   🔍 Risk Factors: {len(result.risk_factors)} identified")
        return True
    except Exception as e:
        print(f"   ❌ Prospect analysis failed: {str(e)}")
        return False


async def test_compliance_monitoring_simple():
    """Simple compliance monitoring test"""
    print("\n⚖️  Testing Compliance Monitoring (Simple)...")
    
    try:
        # Test service status
        status = compliance_ai_service.get_service_status()
        print(f"   ✅ Service Status: {status.get('status', 'unknown')}")
        print(f"   🤖 Enhanced AI: {status.get('enhanced_ai_available', False)}")
        print(f"   📋 Supported Regulations: {len(status.get('supported_regulations', []))}")
        return True
    except Exception as e:
        print(f"   ❌ Compliance test failed: {str(e)}")
        return False


async def main():
    """Main test function"""
    print("🚀 DealVerse OS - Simple AI Integration Test")
    print("=" * 50)
    
    # Test AI status
    ai_configured = await test_ai_status()
    if not ai_configured:
        print("\n⚠️  No AI providers configured, but services should still work with fallbacks")
    
    # Test document analysis
    doc_ok = await test_document_analysis_simple()
    
    # Test prospect analysis
    prospect_ok = await test_prospect_analysis_simple()
    
    # Test compliance monitoring
    compliance_ok = await test_compliance_monitoring_simple()
    
    print("\n" + "=" * 50)
    if doc_ok and prospect_ok and compliance_ok:
        print("🎉 ALL SIMPLE AI TESTS PASSED!")
        print("✅ Document analysis working")
        print("✅ Prospect analysis working")
        print("✅ Compliance monitoring working")
        if ai_configured:
            print("✅ Real AI providers configured")
        else:
            print("⚠️  Using fallback AI (configure API keys for real AI)")
    else:
        print("❌ Some tests failed:")
        if not doc_ok:
            print("   - Document analysis failed")
        if not prospect_ok:
            print("   - Prospect analysis failed")
        if not compliance_ok:
            print("   - Compliance monitoring failed")
    
    print("=" * 50)
    return doc_ok and prospect_ok and compliance_ok


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
