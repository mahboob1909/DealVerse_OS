"""
Test Enhanced Prospect AI Integration
Validates real AI integration for prospect scoring and market analysis
"""
import asyncio
import time
from decimal import Decimal

from app.services.enhanced_prospect_ai import enhanced_prospect_ai
from app.services.prospect_ai import prospect_ai_service
from app.schemas.prospect import ProspectAnalysisRequest


async def test_enhanced_prospect_ai():
    """Test enhanced prospect AI functionality"""
    
    print("🚀 Starting Enhanced Prospect AI Tests")
    print("=" * 60)
    
    # Test 1: AI Configuration
    print("\n📋 Test 1: Prospect AI Configuration")
    print("-" * 40)
    
    try:
        settings = enhanced_prospect_ai.settings
        print(f"✓ AI Settings loaded successfully")
        print(f"  - Preferred provider: {settings.preferred_provider}")
        print(f"  - OpenRouter configured: {bool(settings.openrouter_api_key)}")
        print(f"  - Model: {settings.openrouter_model}")
        print(f"  - Max tokens: {settings.max_tokens}")
        print(f"  - Temperature: {settings.temperature}")
    except Exception as e:
        print(f"✗ Configuration failed: {str(e)}")
    
    # Test 2: Enhanced Prospect Analysis
    print("\n🔍 Test 2: Enhanced Prospect Analysis")
    print("-" * 40)
    
    # Create test prospect request
    test_request = ProspectAnalysisRequest(
        company_name="TechCorp Solutions",
        industry="Technology",
        location="San Francisco, CA",
        revenue=Decimal("150000000"),  # $150M
        employees="500-1000",
        market_cap=Decimal("800000000"),  # $800M
        financial_data={
            "ebitda": 25000000,
            "gross_margin": 0.65,
            "revenue_growth": 0.28,
            "debt_to_equity": 0.35,
            "current_ratio": 2.1
        },
        criteria={
            "target_industry": "technology",
            "min_revenue": 100000000,
            "growth_focus": True
        },
        analysis_type="full"
    )
    
    start_time = time.time()
    
    try:
        print("  Performing enhanced prospect analysis...")
        result = await enhanced_prospect_ai.analyze_prospect_enhanced(test_request)
        
        analysis_time = time.time() - start_time
        
        print(f"✓ Analysis completed in {analysis_time:.2f} seconds")
        print(f"  - AI Score: {result.ai_score}%")
        print(f"  - Confidence Level: {result.confidence_level}")
        print(f"  - Deal Probability: {result.deal_probability}%")
        print(f"  - Estimated Deal Size: ${result.estimated_deal_size:,.0f}")
        print(f"  - Risk Factors: {len(result.risk_factors)} identified")
        print(f"  - Opportunities: {len(result.opportunities)} identified")
        print(f"  - Model Version: {result.model_version}")
        
        # Display detailed scores
        if result.analysis_details:
            print(f"  - Financial Health: {result.analysis_details.get('financial_health', 'N/A')}")
            print(f"  - Market Position: {result.analysis_details.get('market_position', 'N/A')}")
            print(f"  - Growth Potential: {result.analysis_details.get('growth_potential', 'N/A')}")
            print(f"  - Strategic Fit: {result.analysis_details.get('strategic_fit', 'N/A')}")
        
        # Display key insights
        if result.risk_factors:
            print(f"  - Top Risk: {result.risk_factors[0]}")
        if result.opportunities:
            print(f"  - Top Opportunity: {result.opportunities[0]}")
            
    except Exception as e:
        print(f"✗ Enhanced analysis failed: {str(e)}")
    
    # Test 3: Integrated Service Analysis
    print("\n🔧 Test 3: Integrated Prospect Service")
    print("-" * 40)
    
    try:
        print("  Testing integrated prospect AI service...")
        integrated_result = await prospect_ai_service.analyze_prospect(test_request)
        
        print(f"✓ Integrated analysis successful")
        print(f"  - AI Score: {integrated_result.ai_score}%")
        print(f"  - Confidence: {integrated_result.confidence_level}")
        print(f"  - Deal Probability: {integrated_result.deal_probability}%")
        print(f"  - Processing Time: {integrated_result.processing_time:.2f}s")
        
    except Exception as e:
        print(f"✗ Integrated analysis failed: {str(e)}")
    
    # Test 4: Different Analysis Types
    print("\n📊 Test 4: Analysis Type Variations")
    print("-" * 40)
    
    analysis_types = ["financial", "market", "competitive"]
    
    for analysis_type in analysis_types:
        try:
            test_request.analysis_type = analysis_type
            print(f"  Testing {analysis_type} analysis...")
            
            result = await enhanced_prospect_ai.analyze_prospect_enhanced(test_request)
            print(f"  ✓ {analysis_type.title()} analysis: Score {result.ai_score}%")
            
        except Exception as e:
            print(f"  ✗ {analysis_type.title()} analysis failed: {str(e)}")
    
    # Test 5: Error Handling
    print("\n🛡️  Test 5: Error Handling")
    print("-" * 40)
    
    # Test with minimal data
    minimal_request = ProspectAnalysisRequest(
        company_name="Minimal Corp",
        analysis_type="full"
    )
    
    try:
        print("  Testing with minimal data...")
        minimal_result = await enhanced_prospect_ai.analyze_prospect_enhanced(minimal_request)
        print(f"  ✓ Minimal data analysis: Score {minimal_result.ai_score}%")
        print(f"    Confidence: {minimal_result.confidence_level}")
        
    except Exception as e:
        print(f"  ✗ Minimal data test failed: {str(e)}")
    
    print("\n" + "=" * 60)
    print("🎯 Enhanced Prospect AI Tests Complete")
    print("=" * 60)


async def main():
    """Main test execution"""
    await test_enhanced_prospect_ai()


if __name__ == "__main__":
    asyncio.run(main())
