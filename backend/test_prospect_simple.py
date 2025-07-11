"""
Simple test for Enhanced Prospect AI Integration
"""
import asyncio
from decimal import Decimal

from app.services.prospect_ai import prospect_ai_service
from app.schemas.prospect import ProspectAnalysisRequest


async def test_prospect_integration():
    """Test basic prospect AI integration"""
    
    print("🚀 Testing Prospect AI Integration")
    print("=" * 50)
    
    # Create simple test request
    test_request = ProspectAnalysisRequest(
        company_name="Test Corp",
        industry="Technology",
        revenue=Decimal("50000000"),  # $50M
        analysis_type="full"
    )
    
    try:
        print("  Testing integrated prospect service...")
        result = await prospect_ai_service.analyze_prospect(test_request)
        
        print(f"✓ Analysis successful!")
        print(f"  - Company: {test_request.company_name}")
        print(f"  - AI Score: {result.ai_score}%")
        print(f"  - Confidence: {result.confidence_level}")
        print(f"  - Deal Probability: {result.deal_probability}%")
        print(f"  - Processing Time: {result.processing_time:.2f}s")
        print(f"  - Analysis Date: {result.analysis_date}")
        print(f"  - Model Version: {result.model_version}")
        
        if result.risk_factors:
            print(f"  - Risk Factors: {len(result.risk_factors)} identified")
            print(f"    Top Risk: {result.risk_factors[0]}")
        
        if result.opportunities:
            print(f"  - Opportunities: {len(result.opportunities)} identified")
            print(f"    Top Opportunity: {result.opportunities[0]}")
        
        print(f"  - Recommended Approach: {result.recommended_approach}")
        
        return True
        
    except Exception as e:
        print(f"✗ Analysis failed: {str(e)}")
        return False


async def main():
    """Main test execution"""
    success = await test_prospect_integration()
    
    if success:
        print("\n🎯 Prospect AI Integration Test PASSED")
    else:
        print("\n❌ Prospect AI Integration Test FAILED")


if __name__ == "__main__":
    asyncio.run(main())
