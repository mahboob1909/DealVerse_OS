#!/usr/bin/env python3
"""
Simple test for Financial AI integration
Tests the enhanced financial AI service with sample financial model data
"""
import asyncio
import json
import sys
import os
from decimal import Decimal

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from app.schemas.financial_ai import FinancialAIAnalysisRequest
from app.services.financial_model_ai import FinancialModelAIService


async def test_financial_ai_analysis():
    """Test financial AI analysis with sample model data"""

    print("🧪 Testing Financial AI Analysis...")
    print("=" * 50)

    # Create service instance with fallback mode
    financial_model_ai_service = FinancialModelAIService()
    financial_model_ai_service.use_enhanced_ai = False  # Use fallback for testing
    
    # Sample financial model data (DCF model)
    sample_model_data = {
        "model_type": "DCF",
        "model_data": {
            "company_name": "TechCorp Inc.",
            "industry": "Software",
            "revenue_projections": {
                "2024": 10000000,  # $10M
                "2025": 13000000,  # $13M (30% growth)
                "2026": 16250000,  # $16.25M (25% growth)
                "2027": 19500000,  # $19.5M (20% growth)
                "2028": 23400000   # $23.4M (20% growth)
            },
            "ebitda_margins": {
                "2024": 0.15,  # 15%
                "2025": 0.18,  # 18%
                "2026": 0.20,  # 20%
                "2027": 0.22,  # 22%
                "2028": 0.25   # 25%
            },
            "capex_as_percent_revenue": 0.05,  # 5%
            "working_capital_change": 0.02,    # 2% of revenue change
            "tax_rate": 0.25,                  # 25%
            "terminal_growth_rate": 0.03,      # 3%
            "discount_rate": 0.12              # 12% WACC
        },
        "assumptions": {
            "revenue_growth_rates": [0.30, 0.25, 0.20, 0.20],
            "margin_expansion": "Driven by operational efficiency and scale",
            "market_conditions": "Stable growth market with increasing demand",
            "competitive_position": "Strong market leader with defensible moat"
        },
        "inputs": {
            "base_year_revenue": 10000000,
            "projection_years": 5,
            "terminal_multiple": 15.0,
            "debt_to_equity": 0.3
        },
        "outputs": {
            "enterprise_value": 85000000,  # $85M
            "equity_value": 65000000,      # $65M
            "implied_multiple": "8.5x Revenue",
            "irr": 0.28                    # 28%
        }
    }
    
    # Test different analysis types
    analysis_types = ["comprehensive", "validation", "optimization"]
    
    for analysis_type in analysis_types:
        print(f"\n🔍 Testing {analysis_type.upper()} Analysis:")
        print("-" * 30)
        
        try:
            # Create analysis request
            request = FinancialAIAnalysisRequest(
                model_data=sample_model_data,
                analysis_type=analysis_type,
                include_suggestions=True,
                include_validation=True,
                include_scenarios=True
            )
            
            # Perform analysis
            result = await financial_model_ai_service.analyze_financial_model(request)
            
            # Display results
            print(f"✅ Analysis Status: {result.status}")
            print(f"📊 Model Quality Score: {result.ai_insights.model_quality_score}")
            print(f"🎯 Confidence Level: {result.confidence_metrics.confidence_level}")
            print(f"⏱️  Processing Time: {result.processing_time}s")
            print(f"🤖 Model Version: {result.model_version}")
            
            # Show key insights
            print(f"\n💡 Key Insights ({len(result.ai_insights.key_insights)}):")
            for i, insight in enumerate(result.ai_insights.key_insights[:3], 1):
                print(f"   {i}. {insight}")
            
            # Show risk factors
            print(f"\n⚠️  Risk Factors ({len(result.ai_insights.risk_factors)}):")
            for i, risk in enumerate(result.ai_insights.risk_factors[:3], 1):
                print(f"   {i}. {risk}")
            
            # Show optimization opportunities
            print(f"\n🚀 Optimization Opportunities ({len(result.ai_insights.optimization_opportunities)}):")
            for i, opp in enumerate(result.ai_insights.optimization_opportunities[:3], 1):
                print(f"   {i}. {opp}")
            
            # Show validation results
            if result.validation_results:
                validation = result.validation_results
                print(f"\n✅ Validation Results:")
                print(f"   Overall Score: {validation.get('overall_score', 'N/A')}")
                print(f"   Structure Score: {validation.get('structure_score', 'N/A')}")
                print(f"   Validation Passed: {validation.get('validation_passed', 'N/A')}")
            
            print(f"\n{'='*50}")
            
        except Exception as e:
            print(f"❌ Error in {analysis_type} analysis: {str(e)}")
            print(f"Error type: {type(e).__name__}")
            import traceback
            traceback.print_exc()
    
    # Test service status
    print(f"\n🔧 Testing Service Status:")
    print("-" * 30)

    try:
        status = financial_model_ai_service.get_service_status()
        print(f"✅ Service Type: {status['service_type']}")
        print(f"🤖 Enhanced AI Available: {status['enhanced_ai_available']}")
        print(f"📋 Supported Model Types: {', '.join(status['supported_model_types'])}")
        print(f"🔍 Analysis Types: {', '.join(status['analysis_types'])}")
        print(f"📦 Model Version: {status['model_version']}")

    except Exception as e:
        print(f"❌ Error getting service status: {str(e)}")
    
    print(f"\n🎉 Financial AI Testing Complete!")


async def test_model_optimization():
    """Test model optimization functionality"""

    print(f"\n🛠️  Testing Model Optimization:")
    print("-" * 30)

    try:
        from app.schemas.financial_ai import ModelOptimizationRequest
        from uuid import uuid4

        # Create service instance
        financial_model_ai_service = FinancialModelAIService()

        # Create optimization request
        request = ModelOptimizationRequest(
            model_id=uuid4(),
            optimization_focus=["accuracy", "completeness", "scenarios"],
            current_issues=["Missing sensitivity analysis", "Limited scenario coverage"],
            target_confidence_level="high"
        )

        # Get optimization suggestions
        result = await financial_model_ai_service.optimize_model(request)
        
        print(f"✅ Model ID: {result.model_id}")
        print(f"📊 Current Quality Score: {result.current_quality_score}")
        print(f"🎯 Potential Quality Score: {result.potential_quality_score}")
        print(f"📈 Confidence Improvement: {result.confidence_improvement}%")
        
        print(f"\n💡 Optimization Suggestions ({len(result.optimization_suggestions)}):")
        for i, suggestion in enumerate(result.optimization_suggestions, 1):
            print(f"   {i}. [{suggestion.priority.upper()}] {suggestion.suggestion}")
            print(f"      Category: {suggestion.category}, Impact: {suggestion.impact}")
        
        print(f"\n🎯 Priority Actions:")
        for i, action in enumerate(result.priority_actions, 1):
            print(f"   {i}. {action}")
        
        print(f"\n📋 Implementation Roadmap:")
        for step in result.implementation_roadmap:
            print(f"   Step {step['step']}: {step['action']} ({step['effort']})")
        
    except Exception as e:
        print(f"❌ Error in optimization test: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("🚀 Starting Financial AI Integration Tests...")
    print("=" * 60)
    
    # Run the tests
    asyncio.run(test_financial_ai_analysis())
    asyncio.run(test_model_optimization())
    
    print("\n" + "=" * 60)
    print("✨ All Financial AI tests completed!")
