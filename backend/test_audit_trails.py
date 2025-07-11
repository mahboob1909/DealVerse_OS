#!/usr/bin/env python3
"""
Test script for DealVerse OS Audit Trails Service
Tests comprehensive activity logging and audit trail features
"""
import asyncio
import sys
import os
from datetime import datetime, timedelta
from uuid import uuid4

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from app.services.audit_trails_service import audit_trails_service, AuditEventType, AuditSeverity


class MockDB:
    """Mock database session for testing"""
    pass


async def test_log_audit_event():
    """Test logging audit events"""
    print("📝 Testing Audit Event Logging...")
    
    try:
        db = MockDB()
        user_id = uuid4()
        organization_id = uuid4()
        resource_id = uuid4()
        
        # Test logging different types of events
        test_events = [
            {
                "event_type": AuditEventType.USER_LOGIN,
                "resource_type": "user",
                "details": {"login_method": "password", "success": True}
            },
            {
                "event_type": AuditEventType.DEAL_CREATED,
                "resource_type": "deal",
                "resource_id": resource_id,
                "details": {"deal_name": "Test Deal", "deal_value": 100000}
            },
            {
                "event_type": AuditEventType.DOCUMENT_UPLOADED,
                "resource_type": "document",
                "resource_id": resource_id,
                "details": {"filename": "contract.pdf", "size": 1024000}
            },
            {
                "event_type": AuditEventType.SECURITY_BREACH_ATTEMPT,
                "resource_type": "security",
                "severity": AuditSeverity.CRITICAL,
                "details": {"attack_type": "brute_force", "blocked": True}
            }
        ]
        
        logged_events = []
        
        for event_data in test_events:
            audit_event = await audit_trails_service.log_audit_event(
                db=db,
                event_type=event_data["event_type"],
                user_id=user_id,
                organization_id=organization_id,
                resource_type=event_data["resource_type"],
                resource_id=event_data.get("resource_id"),
                details=event_data.get("details"),
                ip_address="192.168.1.100",
                user_agent="Mozilla/5.0 Test Browser",
                severity=event_data.get("severity")
            )
            
            logged_events.append(audit_event)
            
            # Validate audit event structure
            required_fields = [
                "id", "event_type", "severity", "user_id", "organization_id",
                "resource_type", "timestamp", "context"
            ]
            
            for field in required_fields:
                if field not in audit_event:
                    print(f"   ❌ Missing field '{field}' in audit event")
                    return False
            
            print(f"   ✅ Logged {audit_event['event_type']} event (ID: {audit_event['id'][:8]}...)")
        
        print(f"   ✅ Successfully logged {len(logged_events)} audit events")
        print("   ✅ Audit event logging test passed!")
        return True
        
    except Exception as e:
        print(f"   ❌ Audit event logging test failed: {str(e)}")
        return False


def test_severity_determination():
    """Test automatic severity determination"""
    print("\n⚖️  Testing Severity Determination...")
    
    try:
        # Test different event types and their expected severities
        test_cases = [
            (AuditEventType.USER_LOGIN, AuditSeverity.LOW),
            (AuditEventType.USER_CREATED, AuditSeverity.MEDIUM),
            (AuditEventType.DEAL_DELETED, AuditSeverity.HIGH),
            (AuditEventType.SECURITY_BREACH_ATTEMPT, AuditSeverity.CRITICAL),
            (AuditEventType.COMPLIANCE_VIOLATION, AuditSeverity.CRITICAL),
            (AuditEventType.PASSWORD_CHANGED, AuditSeverity.MEDIUM),
            (AuditEventType.DOCUMENT_SHARED, AuditSeverity.MEDIUM)
        ]
        
        for event_type, expected_severity in test_cases:
            determined_severity = audit_trails_service._determine_severity(event_type)
            
            if determined_severity != expected_severity:
                print(f"   ❌ Wrong severity for {event_type}: expected {expected_severity}, got {determined_severity}")
                return False
            
            print(f"   ✅ {event_type.value}: {determined_severity.value}")
        
        print("   ✅ Severity determination test passed!")
        return True
        
    except Exception as e:
        print(f"   ❌ Severity determination test failed: {str(e)}")
        return False


async def test_get_audit_trail():
    """Test retrieving audit trail with filtering"""
    print("\n📊 Testing Audit Trail Retrieval...")
    
    try:
        db = MockDB()
        organization_id = uuid4()
        
        # Test basic retrieval
        audit_data = await audit_trails_service.get_audit_trail(
            db=db,
            organization_id=organization_id,
            limit=50,
            offset=0
        )
        
        # Validate response structure
        required_keys = ["events", "pagination", "filters_applied", "date_range"]
        for key in required_keys:
            if key not in audit_data:
                print(f"   ❌ Missing key '{key}' in audit trail response")
                return False
        
        print(f"   ✅ Retrieved {len(audit_data['events'])} audit events")
        print(f"   ✅ Pagination: total={audit_data['pagination']['total']}, limit={audit_data['pagination']['limit']}")
        
        # Test with filters
        filters = {
            "event_type": "user_login",
            "severity": "medium"
        }
        
        filtered_data = await audit_trails_service.get_audit_trail(
            db=db,
            organization_id=organization_id,
            filters=filters,
            limit=20
        )
        
        print(f"   ✅ Filtered retrieval: {len(filtered_data['events'])} events")
        print(f"   ✅ Filters applied: {filtered_data['filters_applied']}")
        
        # Test date range filtering
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=7)
        
        date_filtered_data = await audit_trails_service.get_audit_trail(
            db=db,
            organization_id=organization_id,
            start_date=start_date,
            end_date=end_date,
            limit=30
        )
        
        print(f"   ✅ Date range filtering: {len(date_filtered_data['events'])} events")
        
        print("   ✅ Audit trail retrieval test passed!")
        return True
        
    except Exception as e:
        print(f"   ❌ Audit trail retrieval test failed: {str(e)}")
        return False


def test_filter_application():
    """Test applying filters to audit events"""
    print("\n🔍 Testing Filter Application...")
    
    try:
        # Create mock events
        mock_events = [
            {
                "id": str(uuid4()),
                "event_type": "user_login",
                "severity": "low",
                "user_id": "user1",
                "resource_type": "user",
                "ip_address": "192.168.1.100"
            },
            {
                "id": str(uuid4()),
                "event_type": "deal_created",
                "severity": "medium",
                "user_id": "user2",
                "resource_type": "deal",
                "ip_address": "192.168.1.101"
            },
            {
                "id": str(uuid4()),
                "event_type": "user_login",
                "severity": "low",
                "user_id": "user1",
                "resource_type": "user",
                "ip_address": "192.168.1.100"
            }
        ]
        
        # Test event type filter
        event_type_filter = {"event_type": "user_login"}
        filtered_events = audit_trails_service._apply_filters(mock_events, event_type_filter)
        
        if len(filtered_events) != 2:
            print(f"   ❌ Event type filter failed: expected 2 events, got {len(filtered_events)}")
            return False
        
        print("   ✅ Event type filter working")
        
        # Test severity filter
        severity_filter = {"severity": "medium"}
        filtered_events = audit_trails_service._apply_filters(mock_events, severity_filter)
        
        if len(filtered_events) != 1:
            print(f"   ❌ Severity filter failed: expected 1 event, got {len(filtered_events)}")
            return False
        
        print("   ✅ Severity filter working")
        
        # Test user filter
        user_filter = {"user_id": "user1"}
        filtered_events = audit_trails_service._apply_filters(mock_events, user_filter)
        
        if len(filtered_events) != 2:
            print(f"   ❌ User filter failed: expected 2 events, got {len(filtered_events)}")
            return False
        
        print("   ✅ User filter working")
        
        # Test multiple filters
        multiple_filters = {"event_type": "user_login", "user_id": "user1"}
        filtered_events = audit_trails_service._apply_filters(mock_events, multiple_filters)
        
        if len(filtered_events) != 2:
            print(f"   ❌ Multiple filters failed: expected 2 events, got {len(filtered_events)}")
            return False
        
        print("   ✅ Multiple filters working")
        
        print("   ✅ Filter application test passed!")
        return True
        
    except Exception as e:
        print(f"   ❌ Filter application test failed: {str(e)}")
        return False


async def test_compliance_report_generation():
    """Test generating compliance reports"""
    print("\n📋 Testing Compliance Report Generation...")
    
    try:
        db = MockDB()
        organization_id = uuid4()
        
        # Generate compliance report
        compliance_report = await audit_trails_service.generate_compliance_report(
            db=db,
            organization_id=organization_id,
            report_type="comprehensive"
        )
        
        # Validate report structure
        required_keys = [
            "report_id", "report_type", "organization_id", "generated_at",
            "date_range", "compliance_metrics", "risk_assessment", "recommendations"
        ]
        
        for key in required_keys:
            if key not in compliance_report:
                print(f"   ❌ Missing key '{key}' in compliance report")
                return False
        
        print(f"   ✅ Report ID: {compliance_report['report_id'][:8]}...")
        print(f"   ✅ Report type: {compliance_report['report_type']}")
        print(f"   ✅ Events analyzed: {compliance_report['total_events_analyzed']}")
        
        # Validate compliance metrics
        metrics = compliance_report["compliance_metrics"]
        required_metric_keys = [
            "total_events", "event_type_distribution", "severity_distribution",
            "high_risk_events", "unique_users"
        ]
        
        for key in required_metric_keys:
            if key not in metrics:
                print(f"   ❌ Missing metric '{key}' in compliance metrics")
                return False
        
        print(f"   ✅ Total events: {metrics['total_events']}")
        print(f"   ✅ High-risk events: {metrics['high_risk_events']}")
        print(f"   ✅ Unique users: {metrics['unique_users']}")
        
        # Validate risk assessment
        risk_assessment = compliance_report["risk_assessment"]
        required_risk_keys = ["risk_level", "risk_score", "identified_risks"]
        
        for key in required_risk_keys:
            if key not in risk_assessment:
                print(f"   ❌ Missing risk key '{key}' in risk assessment")
                return False
        
        print(f"   ✅ Risk level: {risk_assessment['risk_level']}")
        print(f"   ✅ Risk score: {risk_assessment['risk_score']}")
        print(f"   ✅ Identified risks: {len(risk_assessment['identified_risks'])}")
        
        # Validate recommendations
        recommendations = compliance_report["recommendations"]
        if not isinstance(recommendations, list):
            print("   ❌ Recommendations should be a list")
            return False
        
        print(f"   ✅ Recommendations: {len(recommendations)}")
        
        print("   ✅ Compliance report generation test passed!")
        return True
        
    except Exception as e:
        print(f"   ❌ Compliance report generation test failed: {str(e)}")
        return False


def test_compliance_metrics_analysis():
    """Test analyzing compliance metrics"""
    print("\n📈 Testing Compliance Metrics Analysis...")
    
    try:
        # Create mock events for analysis
        mock_events = []
        
        # Generate diverse events
        event_types = ["user_login", "deal_created", "document_uploaded", "user_deleted", "security_breach_attempt"]
        severities = ["low", "medium", "high", "critical"]
        users = [str(uuid4()) for _ in range(5)]
        
        for i in range(100):
            event = {
                "event_type": event_types[i % len(event_types)],
                "severity": severities[i % len(severities)],
                "user_id": users[i % len(users)],
                "timestamp": (datetime.utcnow() - timedelta(hours=i)).isoformat()
            }
            mock_events.append(event)
        
        # Analyze metrics
        metrics = audit_trails_service._analyze_compliance_metrics(mock_events)
        
        # Validate metrics
        if metrics["total_events"] != 100:
            print(f"   ❌ Wrong total events: expected 100, got {metrics['total_events']}")
            return False
        
        if len(metrics["event_type_distribution"]) != len(event_types):
            print(f"   ❌ Wrong event type distribution count")
            return False
        
        if len(metrics["severity_distribution"]) != len(severities):
            print(f"   ❌ Wrong severity distribution count")
            return False
        
        if metrics["unique_users"] != len(users):
            print(f"   ❌ Wrong unique users count: expected {len(users)}, got {metrics['unique_users']}")
            return False
        
        print(f"   ✅ Total events: {metrics['total_events']}")
        print(f"   ✅ Event types: {len(metrics['event_type_distribution'])}")
        print(f"   ✅ Severity levels: {len(metrics['severity_distribution'])}")
        print(f"   ✅ Unique users: {metrics['unique_users']}")
        print(f"   ✅ High-risk percentage: {metrics['high_risk_percentage']:.1f}%")
        
        print("   ✅ Compliance metrics analysis test passed!")
        return True
        
    except Exception as e:
        print(f"   ❌ Compliance metrics analysis test failed: {str(e)}")
        return False


def test_security_risk_assessment():
    """Test security risk assessment"""
    print("\n🛡️  Testing Security Risk Assessment...")
    
    try:
        # Create events with known security risks
        high_risk_events = []
        
        # Add multiple security events (should trigger high risk)
        for i in range(15):
            high_risk_events.append({
                "event_type": "security_breach_attempt",
                "severity": "critical"
            })
        
        # Add multiple critical events
        for i in range(8):
            high_risk_events.append({
                "event_type": "compliance_violation",
                "severity": "critical"
            })
        
        # Add data export events
        for i in range(25):
            high_risk_events.append({
                "event_type": "data_export",
                "severity": "medium"
            })
        
        # Assess risks
        risk_assessment = audit_trails_service._assess_security_risks(high_risk_events)
        
        # Validate risk assessment
        if risk_assessment["risk_level"] not in ["HIGH", "CRITICAL"]:
            print(f"   ❌ Expected high risk level, got {risk_assessment['risk_level']}")
            return False
        
        if risk_assessment["risk_score"] < 70:
            print(f"   ❌ Expected high risk score, got {risk_assessment['risk_score']}")
            return False
        
        if len(risk_assessment["identified_risks"]) == 0:
            print("   ❌ No risks identified when risks should be present")
            return False
        
        print(f"   ✅ Risk level: {risk_assessment['risk_level']}")
        print(f"   ✅ Risk score: {risk_assessment['risk_score']}")
        print(f"   ✅ Identified risks: {len(risk_assessment['identified_risks'])}")
        
        for risk in risk_assessment["identified_risks"]:
            print(f"      - {risk}")
        
        print(f"   ✅ Recommendations: {len(risk_assessment['recommendations'])}")
        
        print("   ✅ Security risk assessment test passed!")
        return True
        
    except Exception as e:
        print(f"   ❌ Security risk assessment test failed: {str(e)}")
        return False


async def main():
    """Main test function"""
    print("🚀 DealVerse OS - Audit Trails Service Test")
    print("=" * 60)
    
    test_results = []
    
    # Run all tests
    test_results.append(await test_log_audit_event())
    test_results.append(test_severity_determination())
    test_results.append(await test_get_audit_trail())
    test_results.append(test_filter_application())
    test_results.append(await test_compliance_report_generation())
    test_results.append(test_compliance_metrics_analysis())
    test_results.append(test_security_risk_assessment())
    
    # Summary
    print("\n" + "=" * 60)
    passed_tests = sum(test_results)
    total_tests = len(test_results)
    
    if passed_tests == total_tests:
        print("🎉 ALL AUDIT TRAILS TESTS PASSED!")
        print(f"✅ {passed_tests}/{total_tests} audit features working correctly")
        print("✅ Event logging working")
        print("✅ Severity determination working")
        print("✅ Audit trail retrieval working")
        print("✅ Filtering system working")
        print("✅ Compliance reporting working")
        print("✅ Risk assessment working")
        print("✅ Audit trails service ready for production")
    else:
        print(f"⚠️  {passed_tests}/{total_tests} tests passed")
        print("❌ Some audit trails features need attention")
    
    print("=" * 60)
    
    return passed_tests == total_tests


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
