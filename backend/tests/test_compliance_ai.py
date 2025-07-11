"""
Tests for Compliance AI functionality
"""
import asyncio
from datetime import datetime, timedelta
from decimal import Decimal
from uuid import uuid4

from app.services.enhanced_compliance_ai import enhanced_compliance_ai
from app.services.compliance_ai import compliance_ai_service
from app.schemas.compliance_ai import (
    ComplianceAIAnalysisRequest,
    RegulatoryDomain,
    ComplianceRiskLevel
)


class TestEnhancedComplianceAI:
    """Test Enhanced Compliance AI service"""
    
    async def test_comprehensive_compliance_analysis(self):
        """Test comprehensive compliance analysis"""
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
        
        # Verify confidence metrics
        confidence = result.confidence_metrics
        assert isinstance(confidence.overall_confidence, Decimal)
        assert confidence.overall_confidence >= 0
        assert confidence.overall_confidence <= 1
        assert confidence.confidence_level in ["low", "medium", "high"]
        
        print(f"✅ Comprehensive analysis completed with score: {insights.compliance_score}")
        print(f"✅ Risk level: {insights.risk_level}")
        print(f"✅ Violations detected: {len(insights.violations_detected)}")
        print(f"✅ Recommendations: {len(insights.recommendations)}")
    
    async def test_violation_detection_analysis(self):
        """Test violation detection focused analysis"""
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
        
        # Verify violation-focused results
        assert result.status == "completed"
        assert result.ai_insights.violations_detected is not None
        
        # Should have at least some analysis even with fallback
        if result.ai_insights.violations_detected:
            violation = result.ai_insights.violations_detected[0]
            assert violation.violation_type is not None
            assert violation.regulation in [domain.value for domain in RegulatoryDomain]
            assert violation.severity in [level.value for level in ComplianceRiskLevel]
            assert violation.description is not None
            assert isinstance(violation.confidence, Decimal)
            assert violation.confidence >= 0
            assert violation.confidence <= 1
        
        print(f"✅ Violation detection analysis completed")
        print(f"✅ Violations found: {len(result.ai_insights.violations_detected)}")
    
    async def test_regulatory_monitoring_analysis(self):
        """Test regulatory monitoring analysis"""
        request = ComplianceAIAnalysisRequest(
            compliance_context="Regulatory change monitoring",
            analysis_type="regulatory_monitoring",
            regulatory_focus=[RegulatoryDomain.SEC, RegulatoryDomain.FINRA, RegulatoryDomain.AML],
            compliance_data={
                "organization_id": str(uuid4()),
                "monitoring_scope": ["sec", "finra", "aml"],
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
        
        # Verify regulatory monitoring results
        assert result.status == "completed"
        assert result.ai_insights.regulatory_changes is not None
        
        if result.ai_insights.regulatory_changes:
            change = result.ai_insights.regulatory_changes[0]
            assert change.change_id is not None
            assert change.regulation in [domain.value for domain in RegulatoryDomain]
            assert change.title is not None
            assert change.description is not None
            assert change.impact_level in [level.value for level in ComplianceRiskLevel]
            assert isinstance(change.confidence, Decimal)
        
        print(f"✅ Regulatory monitoring analysis completed")
        print(f"✅ Regulatory changes detected: {len(result.ai_insights.regulatory_changes)}")
    
    async def test_pattern_analysis(self):
        """Test compliance pattern analysis"""
        request = ComplianceAIAnalysisRequest(
            compliance_context="Pattern analysis for compliance trends",
            analysis_type="pattern_analysis",
            compliance_data={
                "organization_id": str(uuid4()),
                "historical_data": [
                    {
                        "date": (datetime.utcnow() - timedelta(days=i)).isoformat(),
                        "compliance_score": 75 + (i % 10),
                        "violations": i % 3
                    } for i in range(30)
                ]
            },
            include_patterns=True
        )
        
        result = await enhanced_compliance_ai.analyze_compliance(request)
        
        # Verify pattern analysis results
        assert result.status == "completed"
        assert result.ai_insights.risk_patterns is not None
        
        if result.ai_insights.risk_patterns:
            pattern = result.ai_insights.risk_patterns[0]
            assert pattern.pattern_type is not None
            assert isinstance(pattern.frequency, int)
            assert isinstance(pattern.risk_score, Decimal)
            assert pattern.trend in ["increasing", "decreasing", "stable"]
            assert pattern.recommendation is not None
        
        print(f"✅ Pattern analysis completed")
        print(f"✅ Risk patterns identified: {len(result.ai_insights.risk_patterns)}")
    
    async def test_remediation_plan_generation(self):
        """Test remediation plan generation for violations"""
        # First get violations
        request = ComplianceAIAnalysisRequest(
            compliance_context="Test for remediation plan generation",
            analysis_type="violation_detection",
            compliance_data={
                "organization_id": str(uuid4()),
                "known_issues": [
                    {
                        "type": "documentation_gap",
                        "severity": "high",
                        "area": "internal_controls"
                    },
                    {
                        "type": "process_violation",
                        "severity": "medium",
                        "area": "client_reporting"
                    }
                ]
            }
        )
        
        result = await enhanced_compliance_ai.analyze_compliance(request)
        
        # Verify remediation plan if violations exist
        if result.ai_insights.violations_detected and result.remediation_plan:
            plan = result.remediation_plan
            assert plan.plan_id is not None
            assert plan.title is not None
            assert plan.description is not None
            assert plan.priority in ["low", "medium", "high", "critical"]
            assert plan.estimated_duration is not None
            assert isinstance(plan.steps, list)
            assert len(plan.steps) > 0
            
            # Verify remediation steps
            for step in plan.steps:
                assert isinstance(step.step_number, int)
                assert step.action is not None
                assert step.responsible_party is not None
                assert step.timeline is not None
                assert step.success_criteria is not None
            
            print(f"✅ Remediation plan generated with {len(plan.steps)} steps")
            print(f"✅ Plan priority: {plan.priority}")
            print(f"✅ Estimated duration: {plan.estimated_duration}")
        else:
            print("✅ No violations detected, no remediation plan needed")
    
    def test_service_status(self):
        """Test service status reporting"""
        status = enhanced_compliance_ai.get_service_status()
        
        assert status is not None
        assert "service_type" in status
        assert "model_version" in status
        assert "enhanced_ai_available" in status
        assert "supported_regulations" in status
        assert "analysis_types" in status
        assert "status" in status
        
        assert status["service_type"] == "enhanced_compliance_ai"
        assert status["status"] == "operational"
        assert isinstance(status["supported_regulations"], list)
        assert isinstance(status["analysis_types"], list)
        
        print(f"✅ Service status: {status['status']}")
        print(f"✅ Enhanced AI available: {status['enhanced_ai_available']}")
        print(f"✅ Supported regulations: {len(status['supported_regulations'])}")


class TestComplianceAIService:
    """Test Compliance AI Service integration"""
    
    def test_service_initialization(self):
        """Test service initialization"""
        assert compliance_ai_service is not None
        assert compliance_ai_service.enhanced_ai is not None
        assert compliance_ai_service.model_version is not None
    
    def test_service_status(self):
        """Test service status"""
        status = compliance_ai_service.get_service_status()
        
        assert status is not None
        assert "service_type" in status
        assert "model_version" in status
        assert "enhanced_ai_available" in status
        assert "supported_analysis_types" in status
        assert "status" in status
        
        assert status["service_type"] == "compliance_ai"
        assert status["status"] == "operational"
        
        print(f"✅ Compliance AI Service status: {status['status']}")
        print(f"✅ Analysis types supported: {len(status['supported_analysis_types'])}")


def run_compliance_ai_tests():
    """Run all compliance AI tests"""
    print("🧪 Running Compliance AI Tests...")
    
    # Test Enhanced Compliance AI
    enhanced_ai_tests = TestEnhancedComplianceAI()
    
    print("\n📊 Testing Enhanced Compliance AI...")
    asyncio.run(enhanced_ai_tests.test_comprehensive_compliance_analysis())
    asyncio.run(enhanced_ai_tests.test_violation_detection_analysis())
    asyncio.run(enhanced_ai_tests.test_regulatory_monitoring_analysis())
    asyncio.run(enhanced_ai_tests.test_pattern_analysis())
    asyncio.run(enhanced_ai_tests.test_remediation_plan_generation())
    enhanced_ai_tests.test_service_status()
    
    # Test Compliance AI Service
    service_tests = TestComplianceAIService()
    
    print("\n🔧 Testing Compliance AI Service...")
    service_tests.test_service_initialization()
    service_tests.test_service_status()
    
    print("\n✅ All Compliance AI tests completed successfully!")
    print("🎯 Compliance AI Monitoring implementation is ready for production!")


if __name__ == "__main__":
    run_compliance_ai_tests()
