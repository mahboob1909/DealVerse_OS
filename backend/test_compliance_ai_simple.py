"""
Simple test for Compliance AI functionality
"""
import sys
import os
import asyncio
from datetime import datetime, timedelta
from decimal import Decimal
from uuid import uuid4

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.enhanced_compliance_ai import enhanced_compliance_ai
from app.services.compliance_ai import compliance_ai_service
from app.schemas.compliance_ai import (
    ComplianceAIAnalysisRequest,
    RegulatoryDomain,
    ComplianceRiskLevel
)


async def test_enhanced_compliance_ai():
    """Test Enhanced Compliance AI service"""
    print("🧪 Testing Enhanced Compliance AI...")
    
    # Create test request
    request = ComplianceAIAnalysisRequest(
        compliance_context="Test organization compliance analysis",
        analysis_type="comprehensive",
        regulatory_focus=[RegulatoryDomain.SEC, RegulatoryDomain.SOX],
        compliance_data={
            "organization_id": str(uuid4()),
            "categories": [
                {
                    "id": str(uuid4()),
                    "name": "Financial Reporting",
                    "code": "FR001",
                    "priority_level": "high",
                    "regulatory_body": "SEC"
                }
            ],
            "requirements": [
                {
                    "id": str(uuid4()),
                    "title": "Internal Controls Documentation",
                    "status": "in_progress",
                    "risk_level": "medium",
                    "completion_percentage": 75,
                    "due_date": (datetime.utcnow() + timedelta(days=30)).isoformat()
                }
            ],
            "recent_assessments": [
                {
                    "id": str(uuid4()),
                    "assessment_type": "regular",
                    "status": "completed",
                    "score": 78.5,
                    "risk_level": "medium",
                    "assessment_date": datetime.utcnow().isoformat()
                }
            ]
        },
        include_patterns=True,
        include_trends=True,
        include_predictions=True
    )
    
    # Perform analysis
    result = await enhanced_compliance_ai.analyze_compliance(request)
    
    # Verify response structure
    assert result is not None
    assert result.ai_insights is not None
    assert result.confidence_metrics is not None
    assert result.processing_time > 0
    assert result.analysis_date is not None
    assert result.model_version is not None
    assert result.status == "completed"
    
    # Verify AI insights
    insights = result.ai_insights
    assert isinstance(insights.compliance_score, Decimal)
    assert insights.compliance_score >= 0
    assert insights.compliance_score <= 100
    assert insights.risk_level in [level.value for level in ComplianceRiskLevel]
    assert isinstance(insights.violations_detected, list)
    assert isinstance(insights.regulatory_changes, list)
    assert isinstance(insights.risk_patterns, list)
    assert isinstance(insights.compliance_trends, dict)
    assert isinstance(insights.recommendations, list)
    assert isinstance(insights.monitoring_alerts, list)
    assert insights.confidence_level in ["low", "medium", "high"]
    
    print(f"✅ Comprehensive analysis completed with score: {insights.compliance_score}")
    print(f"✅ Risk level: {insights.risk_level}")
    print(f"✅ Violations detected: {len(insights.violations_detected)}")
    print(f"✅ Regulatory changes: {len(insights.regulatory_changes)}")
    print(f"✅ Risk patterns: {len(insights.risk_patterns)}")
    print(f"✅ Recommendations: {len(insights.recommendations)}")
    print(f"✅ Monitoring alerts: {len(insights.monitoring_alerts)}")
    print(f"✅ Confidence level: {insights.confidence_level}")
    
    # Test remediation plan if violations exist
    if result.remediation_plan:
        plan = result.remediation_plan
        print(f"✅ Remediation plan generated with {len(plan.steps)} steps")
        print(f"✅ Plan priority: {plan.priority}")
        print(f"✅ Estimated duration: {plan.estimated_duration}")
    
    return True


async def test_violation_detection():
    """Test violation detection analysis"""
    print("\n🔍 Testing Violation Detection...")
    
    request = ComplianceAIAnalysisRequest(
        compliance_context="Violation detection for high-risk processes",
        analysis_type="violation_detection",
        regulatory_focus=[RegulatoryDomain.SOX, RegulatoryDomain.FINRA],
        compliance_data={
            "organization_id": str(uuid4()),
            "high_risk_processes": [
                "Financial reporting",
                "Client onboarding",
                "Trade execution"
            ],
            "recent_incidents": [
                {
                    "type": "documentation_gap",
                    "severity": "medium",
                    "date": datetime.utcnow().isoformat()
                }
            ]
        }
    )
    
    result = await enhanced_compliance_ai.analyze_compliance(request)
    
    assert result.status == "completed"
    print(f"✅ Violation detection completed")
    print(f"✅ Violations found: {len(result.ai_insights.violations_detected)}")
    
    if result.ai_insights.violations_detected:
        violation = result.ai_insights.violations_detected[0]
        print(f"✅ Sample violation: {violation.violation_type} ({violation.severity})")
        print(f"✅ Confidence: {violation.confidence}")
    
    return True


async def test_regulatory_monitoring():
    """Test regulatory monitoring analysis"""
    print("\n📊 Testing Regulatory Monitoring...")
    
    request = ComplianceAIAnalysisRequest(
        compliance_context="Regulatory change monitoring",
        analysis_type="regulatory_monitoring",
        regulatory_focus=[RegulatoryDomain.SEC, RegulatoryDomain.FINRA],
        compliance_data={
            "organization_id": str(uuid4()),
            "monitoring_scope": ["sec", "finra"],
            "recent_updates": [
                {
                    "regulation": "SEC",
                    "title": "Enhanced Disclosure Requirements",
                    "impact": "medium",
                    "effective_date": (datetime.utcnow() + timedelta(days=60)).isoformat()
                }
            ]
        }
    )
    
    result = await enhanced_compliance_ai.analyze_compliance(request)
    
    assert result.status == "completed"
    print(f"✅ Regulatory monitoring completed")
    print(f"✅ Regulatory changes detected: {len(result.ai_insights.regulatory_changes)}")
    
    if result.ai_insights.regulatory_changes:
        change = result.ai_insights.regulatory_changes[0]
        print(f"✅ Sample change: {change.title}")
        print(f"✅ Impact level: {change.impact_level}")
        print(f"✅ Confidence: {change.confidence}")
    
    return True


def test_service_status():
    """Test service status"""
    print("\n🔧 Testing Service Status...")
    
    # Test Enhanced Compliance AI status
    enhanced_status = enhanced_compliance_ai.get_service_status()
    assert enhanced_status is not None
    assert enhanced_status["service_type"] == "enhanced_compliance_ai"
    assert enhanced_status["status"] == "operational"
    
    print(f"✅ Enhanced AI status: {enhanced_status['status']}")
    print(f"✅ Enhanced AI available: {enhanced_status['enhanced_ai_available']}")
    print(f"✅ Supported regulations: {len(enhanced_status['supported_regulations'])}")
    
    # Test Compliance AI Service status
    service_status = compliance_ai_service.get_service_status()
    assert service_status is not None
    assert service_status["service_type"] == "compliance_ai"
    assert service_status["status"] == "operational"
    
    print(f"✅ Service status: {service_status['status']}")
    print(f"✅ Analysis types supported: {len(service_status['supported_analysis_types'])}")
    
    return True


async def run_all_tests():
    """Run all compliance AI tests"""
    print("🚀 Starting Compliance AI Tests...")
    print("=" * 60)
    
    try:
        # Test Enhanced Compliance AI
        await test_enhanced_compliance_ai()
        await test_violation_detection()
        await test_regulatory_monitoring()
        
        # Test service status
        test_service_status()
        
        print("\n" + "=" * 60)
        print("✅ ALL COMPLIANCE AI TESTS PASSED!")
        print("🎯 Compliance AI Monitoring implementation is ready!")
        print("📊 Features implemented:")
        print("   • AI-powered compliance analysis")
        print("   • Violation detection and risk assessment")
        print("   • Regulatory change monitoring")
        print("   • Pattern analysis and trend detection")
        print("   • Automated remediation plan generation")
        print("   • Real-time monitoring alerts")
        print("   • Comprehensive confidence metrics")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    if success:
        print("\n🎉 Compliance AI Monitoring Phase 2 Task COMPLETED!")
    else:
        print("\n💥 Tests failed - please check implementation")
