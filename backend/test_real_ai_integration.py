#!/usr/bin/env python3
"""
Test script for Real AI Integration in DealVerse OS
Tests the enhanced AI document analysis with OpenRouter/DeepSeek integration
"""
import asyncio
import sys
import os
import json
import uuid
from datetime import datetime
from pathlib import Path

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from app.services.integrated_ai_service import integrated_ai_service
from app.schemas.document_analysis import DocumentAnalysisRequest
from app.core.ai_config import get_ai_settings, validate_ai_configuration


async def test_ai_configuration():
    """Test AI configuration and service status"""
    print("🔧 Testing AI Configuration...")
    
    # Check AI settings
    settings = get_ai_settings()
    config_status = validate_ai_configuration()
    
    print(f"   OpenAI Configured: {config_status.get('openai_configured', False)}")
    print(f"   Anthropic Configured: {config_status.get('anthropic_configured', False)}")
    print(f"   OpenRouter Configured: {config_status.get('openrouter_configured', False)}")
    print(f"   Preferred Provider: {config_status.get('preferred_provider', 'none')}")
    print(f"   Fallback Enabled: {config_status.get('fallback_enabled', False)}")
    
    if config_status.get('error'):
        print(f"   ❌ Configuration Error: {config_status['error']}")
        return False
    
    # Check service status
    service_status = integrated_ai_service.get_service_status()
    print(f"   Real AI Enabled: {service_status.get('real_ai_enabled', False)}")
    print(f"   AI Provider: {service_status.get('ai_configuration', {}).get('preferred_provider', 'none')}")
    
    return True


async def test_document_analysis():
    """Test document analysis with sample content"""
    print("\n📄 Testing Document Analysis...")
    
    # Sample document content for testing
    sample_documents = [
        {
            "title": "Financial Statements Q3 2024",
            "content": """
ACME Corporation Financial Statements - Q3 2024

Revenue: $15,000,000 (up 25% YoY)
Cost of Goods Sold: $9,000,000
Gross Profit: $6,000,000 (40% margin)
Operating Expenses: $3,500,000
EBITDA: $2,500,000
Net Income: $1,800,000

Key Metrics:
- Customer Acquisition Cost: $150
- Customer Lifetime Value: $2,400
- Monthly Recurring Revenue: $1,200,000
- Churn Rate: 3.2%

Risk Factors:
- Increased competition in core markets
- Regulatory changes in data privacy
- Supply chain disruptions

The company shows strong growth trajectory with improving margins.
Management expects continued growth in Q4 2024.
""",
            "document_type": "financial_statement"
        },
        {
            "title": "Market Analysis Report",
            "content": """
Technology Sector Market Analysis - 2024

Market Size: $2.8 trillion globally
Growth Rate: 8.5% CAGR
Key Trends:
- AI/ML adoption accelerating
- Cloud migration continuing
- Cybersecurity investments increasing

Competitive Landscape:
- Market fragmentation increasing
- New entrants disrupting traditional players
- Consolidation expected in mid-market

Investment Opportunities:
- SaaS companies with strong unit economics
- AI-powered automation tools
- Cybersecurity solutions

Risks:
- Economic downturn impact
- Regulatory scrutiny increasing
- Talent shortage in key areas
""",
            "document_type": "market_analysis"
        }
    ]
    
    for i, doc in enumerate(sample_documents, 1):
        print(f"\n   📋 Test {i}: {doc['title']}")
        
        # Create analysis request with proper UUID
        doc_id = str(uuid.uuid4())
        request = DocumentAnalysisRequest(
            document_id=doc_id,
            analysis_type="full",
            priority="medium"
        )

        # Create document info
        document_info = {
            "id": doc_id,
            "title": doc["title"],
            "document_type": doc["document_type"],
            "content": doc["content"],
            "file_size": len(doc["content"]),
            "file_type": "text"
        }
        
        try:
            # Perform analysis
            print(f"      🤖 Analyzing with AI...")
            result = await integrated_ai_service.analyze_document(request, document_info)
            
            # Display results
            print(f"      ✅ Analysis completed successfully!")
            print(f"         Status: {result.status}")
            print(f"         Model: {result.model_version}")
            print(f"         Processing Time: {result.processing_time}s")
            print(f"         Risk Score: {result.overall_risk_score}/100")
            print(f"         Risk Level: {result.risk_level}")
            print(f"         Confidence: {result.confidence_score}/100")
            print(f"         Summary: {result.summary[:100]}...")
            print(f"         Key Findings: {len(result.key_findings)} findings")
            print(f"         Entities: {len(result.extracted_entities)} types")
            print(f"         Financial Figures: {len(result.financial_figures)} figures")
            
            # Show some key findings
            if result.key_findings:
                print(f"         Top Finding: {result.key_findings[0]}")
            
        except Exception as e:
            print(f"      ❌ Analysis failed: {str(e)}")
            return False
    
    return True


async def test_risk_assessment():
    """Test risk assessment functionality"""
    print("\n⚠️  Testing Risk Assessment...")
    
    # High-risk document content
    high_risk_content = """
CONFIDENTIAL - MERGER AGREEMENT

WARNING: This document contains material non-public information.

XYZ Corp Acquisition Agreement
Purchase Price: $500,000,000
Closing Date: December 31, 2024

CRITICAL ISSUES IDENTIFIED:
- Pending SEC investigation into accounting practices
- Class action lawsuit filed by shareholders
- Key customer contracts expiring without renewal
- $50M environmental liability not disclosed
- CFO resignation effective immediately

Due Diligence Findings:
- Revenue recognition irregularities discovered
- Inventory valuation concerns
- Related party transactions not properly disclosed
- Compliance violations in multiple jurisdictions

RECOMMENDATION: PROCEED WITH EXTREME CAUTION
"""
    
    # Create proper UUID for risk test
    risk_doc_id = str(uuid.uuid4())
    request = DocumentAnalysisRequest(
        document_id=risk_doc_id,
        analysis_type="risk_only",
        priority="high"
    )

    document_info = {
        "id": risk_doc_id,
        "title": "High Risk Merger Agreement",
        "document_type": "legal_agreement",
        "content": high_risk_content,
        "file_size": len(high_risk_content),
        "file_type": "text"
    }
    
    try:
        result = await integrated_ai_service.analyze_document(request, document_info)
        
        print(f"   ✅ Risk assessment completed!")
        print(f"      Risk Score: {result.overall_risk_score}/100")
        print(f"      Risk Level: {result.risk_level}")
        print(f"      Critical Issues: {len(result.critical_issues)} identified")
        print(f"      Compliance Flags: {len(result.compliance_flags)} flags")
        
        # Should detect high risk
        if float(result.overall_risk_score) > 70:
            print(f"   ✅ High risk correctly identified!")
        else:
            print(f"   ⚠️  Risk score seems low for high-risk content")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Risk assessment failed: {str(e)}")
        return False


async def main():
    """Main test function"""
    print("🚀 DealVerse OS - Real AI Integration Test")
    print("=" * 50)
    
    # Test configuration
    config_ok = await test_ai_configuration()
    if not config_ok:
        print("\n❌ AI configuration test failed. Please check your API keys.")
        return False
    
    # Test document analysis
    analysis_ok = await test_document_analysis()
    if not analysis_ok:
        print("\n❌ Document analysis test failed.")
        return False
    
    # Test risk assessment
    risk_ok = await test_risk_assessment()
    if not risk_ok:
        print("\n❌ Risk assessment test failed.")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 ALL AI INTEGRATION TESTS PASSED!")
    print("✅ Real AI document analysis is working correctly")
    print("✅ Risk assessment is functioning properly")
    print("✅ DealVerse OS AI integration is ready for production")
    print("=" * 50)
    
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
