#!/usr/bin/env python3
"""
Audit Trails Service for DealVerse OS
Provides comprehensive activity logging and audit trail features for compliance
"""
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from uuid import UUID, uuid4
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc, asc
from enum import Enum

import logging

logger = logging.getLogger(__name__)


class AuditEventType(str, Enum):
    """Audit event types for categorization"""
    # User actions
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    USER_CREATED = "user_created"
    USER_UPDATED = "user_updated"
    USER_DELETED = "user_deleted"
    PASSWORD_CHANGED = "password_changed"
    
    # Deal actions
    DEAL_CREATED = "deal_created"
    DEAL_UPDATED = "deal_updated"
    DEAL_DELETED = "deal_deleted"
    DEAL_STAGE_CHANGED = "deal_stage_changed"
    DEAL_VALUE_CHANGED = "deal_value_changed"
    
    # Client actions
    CLIENT_CREATED = "client_created"
    CLIENT_UPDATED = "client_updated"
    CLIENT_DELETED = "client_deleted"
    
    # Document actions
    DOCUMENT_UPLOADED = "document_uploaded"
    DOCUMENT_DOWNLOADED = "document_downloaded"
    DOCUMENT_DELETED = "document_deleted"
    DOCUMENT_SHARED = "document_shared"
    
    # Financial model actions
    MODEL_CREATED = "model_created"
    MODEL_UPDATED = "model_updated"
    MODEL_DELETED = "model_deleted"
    MODEL_EXPORTED = "model_exported"
    
    # Presentation actions
    PRESENTATION_CREATED = "presentation_created"
    PRESENTATION_UPDATED = "presentation_updated"
    PRESENTATION_DELETED = "presentation_deleted"
    PRESENTATION_EXPORTED = "presentation_exported"
    
    # Compliance actions
    COMPLIANCE_CHECK = "compliance_check"
    COMPLIANCE_VIOLATION = "compliance_violation"
    COMPLIANCE_REMEDIATION = "compliance_remediation"
    
    # System actions
    SYSTEM_BACKUP = "system_backup"
    SYSTEM_RESTORE = "system_restore"
    SYSTEM_MAINTENANCE = "system_maintenance"
    
    # Security actions
    SECURITY_BREACH_ATTEMPT = "security_breach_attempt"
    PERMISSION_DENIED = "permission_denied"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    
    # Data actions
    DATA_EXPORT = "data_export"
    DATA_IMPORT = "data_import"
    DATA_DELETION = "data_deletion"
    
    # Report actions
    REPORT_GENERATED = "report_generated"
    REPORT_DOWNLOADED = "report_downloaded"


class AuditSeverity(str, Enum):
    """Audit event severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AuditTrailsService:
    """Service for comprehensive audit trails and activity logging"""
    
    def __init__(self):
        self.retention_days = 2555  # 7 years for compliance
        self.high_risk_events = {
            AuditEventType.USER_DELETED,
            AuditEventType.DEAL_DELETED,
            AuditEventType.CLIENT_DELETED,
            AuditEventType.DOCUMENT_DELETED,
            AuditEventType.DATA_DELETION,
            AuditEventType.SECURITY_BREACH_ATTEMPT,
            AuditEventType.COMPLIANCE_VIOLATION,
            AuditEventType.SUSPICIOUS_ACTIVITY
        }
    
    async def log_audit_event(
        self,
        db: Session,
        event_type: AuditEventType,
        user_id: Optional[UUID],
        organization_id: UUID,
        resource_type: str,
        resource_id: Optional[UUID] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        severity: Optional[AuditSeverity] = None
    ) -> Dict[str, Any]:
        """Log an audit event with comprehensive details"""
        
        try:
            # Determine severity if not provided
            if severity is None:
                severity = self._determine_severity(event_type)
            
            # Create audit event record
            audit_event = {
                "id": str(uuid4()),
                "event_type": event_type.value,
                "severity": severity.value,
                "user_id": str(user_id) if user_id else None,
                "organization_id": str(organization_id),
                "resource_type": resource_type,
                "resource_id": str(resource_id) if resource_id else None,
                "timestamp": datetime.utcnow().isoformat(),
                "ip_address": ip_address,
                "user_agent": user_agent,
                "details": details or {},
                "session_id": self._get_session_id(),
                "correlation_id": str(uuid4())
            }
            
            # Add contextual information
            audit_event["context"] = await self._gather_context(
                db, user_id, organization_id, resource_type, resource_id
            )
            
            # Store the audit event (in a real implementation, this would go to a database)
            # For now, we'll log it and return the event
            logger.info(f"Audit Event: {json.dumps(audit_event, indent=2)}")
            
            # Check for compliance violations or security concerns
            await self._check_compliance_rules(audit_event)
            
            # Trigger alerts for high-severity events
            if severity in [AuditSeverity.HIGH, AuditSeverity.CRITICAL]:
                await self._trigger_security_alert(audit_event)
            
            return audit_event
            
        except Exception as e:
            logger.error(f"Failed to log audit event: {str(e)}")
            # Audit logging should never fail silently
            raise
    
    def _determine_severity(self, event_type: AuditEventType) -> AuditSeverity:
        """Determine the severity level of an audit event"""

        # Check critical events first (highest priority)
        critical_events = {
            AuditEventType.SECURITY_BREACH_ATTEMPT,
            AuditEventType.COMPLIANCE_VIOLATION,
            AuditEventType.SYSTEM_RESTORE,
            AuditEventType.SUSPICIOUS_ACTIVITY
        }

        if event_type in critical_events:
            return AuditSeverity.CRITICAL

        # Then check high-risk events
        if event_type in self.high_risk_events:
            return AuditSeverity.HIGH
        
        medium_events = {
            AuditEventType.USER_CREATED,
            AuditEventType.USER_UPDATED,
            AuditEventType.PASSWORD_CHANGED,
            AuditEventType.DEAL_STAGE_CHANGED,
            AuditEventType.DEAL_VALUE_CHANGED,
            AuditEventType.DOCUMENT_SHARED,
            AuditEventType.DATA_EXPORT,
            AuditEventType.PERMISSION_DENIED
        }
        
        if event_type in medium_events:
            return AuditSeverity.MEDIUM
        
        return AuditSeverity.LOW
    
    async def _gather_context(
        self,
        db: Session,
        user_id: Optional[UUID],
        organization_id: UUID,
        resource_type: str,
        resource_id: Optional[UUID]
    ) -> Dict[str, Any]:
        """Gather contextual information for the audit event"""
        
        context = {
            "timestamp_utc": datetime.utcnow().isoformat(),
            "environment": "production",  # This would be configurable
            "application_version": "1.0.0",  # This would come from config
            "resource_type": resource_type
        }
        
        # Add user context if available
        if user_id:
            # In a real implementation, we'd fetch user details from the database
            context["user_context"] = {
                "user_id": str(user_id),
                "organization_id": str(organization_id),
                "roles": ["user"],  # Would fetch from database
                "permissions": []   # Would fetch from database
            }
        
        # Add resource context if available
        if resource_id:
            context["resource_context"] = {
                "resource_id": str(resource_id),
                "resource_type": resource_type
            }
        
        return context
    
    def _get_session_id(self) -> str:
        """Get the current session ID (placeholder implementation)"""
        # In a real implementation, this would extract the session ID from the request context
        return str(uuid4())
    
    async def _check_compliance_rules(self, audit_event: Dict[str, Any]) -> None:
        """Check audit event against compliance rules"""
        
        event_type = audit_event["event_type"]
        severity = audit_event["severity"]
        
        # Example compliance rules
        compliance_violations = []
        
        # Rule: High-risk operations require approval
        if event_type in [e.value for e in self.high_risk_events]:
            if not audit_event["details"].get("approval_id"):
                compliance_violations.append("High-risk operation performed without approval")
        
        # Rule: Data exports must be justified
        if event_type == AuditEventType.DATA_EXPORT.value:
            if not audit_event["details"].get("justification"):
                compliance_violations.append("Data export performed without justification")
        
        # Rule: Critical events require additional verification
        if severity == AuditSeverity.CRITICAL.value:
            if not audit_event["details"].get("verification_method"):
                compliance_violations.append("Critical operation performed without additional verification")
        
        # Log compliance violations
        if compliance_violations:
            violation_event = {
                "id": str(uuid4()),
                "event_type": AuditEventType.COMPLIANCE_VIOLATION.value,
                "severity": AuditSeverity.HIGH.value,
                "original_event_id": audit_event["id"],
                "violations": compliance_violations,
                "timestamp": datetime.utcnow().isoformat()
            }
            logger.warning(f"Compliance Violation: {json.dumps(violation_event, indent=2)}")
    
    async def _trigger_security_alert(self, audit_event: Dict[str, Any]) -> None:
        """Trigger security alerts for high-severity events"""
        
        alert = {
            "alert_id": str(uuid4()),
            "event_id": audit_event["id"],
            "alert_type": "security",
            "severity": audit_event["severity"],
            "event_type": audit_event["event_type"],
            "timestamp": datetime.utcnow().isoformat(),
            "organization_id": audit_event["organization_id"],
            "user_id": audit_event.get("user_id"),
            "ip_address": audit_event.get("ip_address"),
            "description": f"High-severity audit event: {audit_event['event_type']}"
        }
        
        # In a real implementation, this would send notifications to security team
        logger.warning(f"Security Alert: {json.dumps(alert, indent=2)}")
    
    async def get_audit_trail(
        self,
        db: Session,
        organization_id: UUID,
        filters: Optional[Dict[str, Any]] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Retrieve audit trail with filtering and pagination"""
        
        # Set default date range if not provided
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        # In a real implementation, this would query the audit database
        # For now, we'll return a mock response
        mock_events = self._generate_mock_audit_events(organization_id, start_date, end_date)
        
        # Apply filters
        if filters:
            mock_events = self._apply_filters(mock_events, filters)
        
        # Apply pagination
        total_events = len(mock_events)
        paginated_events = mock_events[offset:offset + limit]
        
        return {
            "events": paginated_events,
            "pagination": {
                "total": total_events,
                "limit": limit,
                "offset": offset,
                "has_more": offset + limit < total_events
            },
            "filters_applied": filters or {},
            "date_range": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            }
        }
    
    def _generate_mock_audit_events(
        self,
        organization_id: UUID,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """Generate mock audit events for testing"""
        
        events = []
        current_date = start_date
        
        while current_date <= end_date:
            # Generate 2-5 events per day
            daily_events = 2 + (hash(str(current_date.date())) % 4)
            
            for i in range(daily_events):
                event_time = current_date + timedelta(hours=i * 6, minutes=i * 15)
                
                event = {
                    "id": str(uuid4()),
                    "event_type": list(AuditEventType)[i % len(AuditEventType)].value,
                    "severity": list(AuditSeverity)[i % len(AuditSeverity)].value,
                    "user_id": str(uuid4()),
                    "organization_id": str(organization_id),
                    "resource_type": ["deal", "client", "document", "user"][i % 4],
                    "resource_id": str(uuid4()),
                    "timestamp": event_time.isoformat(),
                    "ip_address": f"192.168.1.{100 + i}",
                    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "details": {
                        "action": f"Sample action {i}",
                        "previous_value": f"old_value_{i}",
                        "new_value": f"new_value_{i}"
                    }
                }
                events.append(event)
            
            current_date += timedelta(days=1)
        
        return sorted(events, key=lambda x: x["timestamp"], reverse=True)
    
    def _apply_filters(self, events: List[Dict[str, Any]], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Apply filters to audit events"""
        
        filtered_events = events
        
        if "event_type" in filters:
            filtered_events = [e for e in filtered_events if e["event_type"] == filters["event_type"]]
        
        if "severity" in filters:
            filtered_events = [e for e in filtered_events if e["severity"] == filters["severity"]]
        
        if "user_id" in filters:
            filtered_events = [e for e in filtered_events if e["user_id"] == filters["user_id"]]
        
        if "resource_type" in filters:
            filtered_events = [e for e in filtered_events if e["resource_type"] == filters["resource_type"]]
        
        if "ip_address" in filters:
            filtered_events = [e for e in filtered_events if e["ip_address"] == filters["ip_address"]]
        
        return filtered_events
    
    async def generate_compliance_report(
        self,
        db: Session,
        organization_id: UUID,
        report_type: str = "comprehensive",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Generate a compliance report based on audit trails"""
        
        # Set default date range
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=90)
        
        # Get audit trail data
        audit_data = await self.get_audit_trail(
            db=db,
            organization_id=organization_id,
            start_date=start_date,
            end_date=end_date,
            limit=10000  # Get all events for analysis
        )
        
        events = audit_data["events"]
        
        # Analyze events for compliance metrics
        compliance_metrics = self._analyze_compliance_metrics(events)
        
        # Generate risk assessment
        risk_assessment = self._assess_security_risks(events)
        
        # Generate recommendations
        recommendations = self._generate_compliance_recommendations(compliance_metrics, risk_assessment)
        
        return {
            "report_id": str(uuid4()),
            "report_type": report_type,
            "organization_id": str(organization_id),
            "generated_at": datetime.utcnow().isoformat(),
            "date_range": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "compliance_metrics": compliance_metrics,
            "risk_assessment": risk_assessment,
            "recommendations": recommendations,
            "total_events_analyzed": len(events)
        }
    
    def _analyze_compliance_metrics(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze events for compliance metrics"""
        
        total_events = len(events)
        
        # Event type distribution
        event_types = {}
        for event in events:
            event_type = event["event_type"]
            event_types[event_type] = event_types.get(event_type, 0) + 1
        
        # Severity distribution
        severity_counts = {}
        for event in events:
            severity = event["severity"]
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        # High-risk events
        high_risk_count = len([e for e in events if e["event_type"] in [et.value for et in self.high_risk_events]])
        
        # User activity
        user_activity = {}
        for event in events:
            user_id = event.get("user_id")
            if user_id:
                user_activity[user_id] = user_activity.get(user_id, 0) + 1
        
        # Time-based analysis
        hourly_activity = {}
        for event in events:
            hour = datetime.fromisoformat(event["timestamp"]).hour
            hourly_activity[hour] = hourly_activity.get(hour, 0) + 1
        
        return {
            "total_events": total_events,
            "event_type_distribution": event_types,
            "severity_distribution": severity_counts,
            "high_risk_events": high_risk_count,
            "high_risk_percentage": (high_risk_count / total_events * 100) if total_events > 0 else 0,
            "unique_users": len(user_activity),
            "most_active_users": sorted(user_activity.items(), key=lambda x: x[1], reverse=True)[:5],
            "peak_activity_hours": sorted(hourly_activity.items(), key=lambda x: x[1], reverse=True)[:3]
        }
    
    def _assess_security_risks(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Assess security risks based on audit events"""
        
        risks = []
        risk_score = 0
        
        # Check for suspicious patterns
        security_events = [e for e in events if e["event_type"] in [
            AuditEventType.SECURITY_BREACH_ATTEMPT.value,
            AuditEventType.PERMISSION_DENIED.value,
            AuditEventType.SUSPICIOUS_ACTIVITY.value
        ]]
        
        if len(security_events) > 10:
            risks.append("High number of security-related events detected")
            risk_score += 30
        
        # Check for unusual activity patterns
        critical_events = [e for e in events if e["severity"] == AuditSeverity.CRITICAL.value]
        if len(critical_events) > 5:
            risks.append("Multiple critical events detected")
            risk_score += 40
        
        # Check for data export activities
        export_events = [e for e in events if e["event_type"] == AuditEventType.DATA_EXPORT.value]
        if len(export_events) > 20:
            risks.append("High volume of data exports")
            risk_score += 20
        
        # Check for deletion activities
        deletion_events = [e for e in events if "deleted" in e["event_type"]]
        if len(deletion_events) > 10:
            risks.append("High number of deletion operations")
            risk_score += 25
        
        # Determine risk level
        if risk_score >= 70:
            risk_level = "HIGH"
        elif risk_score >= 40:
            risk_level = "MEDIUM"
        elif risk_score >= 20:
            risk_level = "LOW"
        else:
            risk_level = "MINIMAL"
        
        return {
            "risk_level": risk_level,
            "risk_score": risk_score,
            "identified_risks": risks,
            "security_events_count": len(security_events),
            "critical_events_count": len(critical_events),
            "recommendations": self._get_risk_recommendations(risk_level, risks)
        }
    
    def _get_risk_recommendations(self, risk_level: str, risks: List[str]) -> List[str]:
        """Get recommendations based on risk assessment"""
        
        recommendations = []
        
        if risk_level in ["HIGH", "CRITICAL"]:
            recommendations.extend([
                "Implement immediate security review",
                "Enable enhanced monitoring",
                "Require additional authentication for high-risk operations",
                "Conduct security audit"
            ])
        
        if "High number of security-related events" in risks:
            recommendations.append("Review and strengthen access controls")
        
        if "High volume of data exports" in risks:
            recommendations.append("Implement data export approval workflow")
        
        if "High number of deletion operations" in risks:
            recommendations.append("Require approval for deletion operations")
        
        return recommendations
    
    def _generate_compliance_recommendations(
        self,
        compliance_metrics: Dict[str, Any],
        risk_assessment: Dict[str, Any]
    ) -> List[str]:
        """Generate compliance recommendations"""
        
        recommendations = []
        
        # Based on compliance metrics
        if compliance_metrics["high_risk_percentage"] > 10:
            recommendations.append("Reduce high-risk operations through process improvements")
        
        if compliance_metrics["unique_users"] < 5:
            recommendations.append("Consider implementing role-based access controls")
        
        # Based on risk assessment
        recommendations.extend(risk_assessment["recommendations"])
        
        # General compliance recommendations
        recommendations.extend([
            "Implement regular audit trail reviews",
            "Establish data retention policies",
            "Create incident response procedures",
            "Conduct regular compliance training"
        ])
        
        return list(set(recommendations))  # Remove duplicates


# Create global instance
audit_trails_service = AuditTrailsService()
