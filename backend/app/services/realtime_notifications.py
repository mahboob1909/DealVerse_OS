"""
Real-time Notification Service for DealVerse OS
Integrates with WebSocket manager to send live updates
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from uuid import UUID

from app.services.websocket_manager import websocket_manager

logger = logging.getLogger(__name__)


class RealtimeNotificationService:
    """Service for sending real-time notifications via WebSocket"""
    
    def __init__(self):
        self.websocket_manager = websocket_manager
    
    async def notify_document_upload_started(
        self, 
        document_id: str, 
        filename: str, 
        user_id: str,
        organization_id: str
    ):
        """Notify organization about document upload start"""
        message = {
            "type": "document_upload_started",
            "document_id": document_id,
            "filename": filename,
            "uploaded_by": user_id,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "uploading"
        }
        
        await self.websocket_manager.broadcast_to_organization(
            message, organization_id, exclude_user=user_id
        )
    
    async def notify_document_upload_completed(
        self, 
        document_id: str, 
        filename: str, 
        file_size: int,
        processing_results: Dict[str, Any],
        user_id: str,
        organization_id: str
    ):
        """Notify organization about successful document upload"""
        message = {
            "type": "document_upload_completed",
            "document_id": document_id,
            "filename": filename,
            "file_size": file_size,
            "processing_results": {
                "text_extracted": processing_results.get("extraction_successful", False),
                "word_count": processing_results.get("word_count", 0),
                "security_scan_passed": processing_results.get("security_scan_passed", True)
            },
            "uploaded_by": user_id,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "completed"
        }
        
        await self.websocket_manager.broadcast_to_organization(
            message, organization_id, exclude_user=user_id
        )
    
    async def notify_document_analysis_started(
        self, 
        document_id: str, 
        analysis_type: str,
        estimated_duration: int = None
    ):
        """Notify about document analysis start"""
        message = {
            "type": "document_analysis_started",
            "document_id": document_id,
            "analysis_type": analysis_type,
            "estimated_duration_seconds": estimated_duration,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "analyzing"
        }
        
        # Notify document collaborators
        await self.websocket_manager.notify_document_analysis_update(
            document_id, "started", progress=0
        )
        
        # Also send detailed message to document room
        await self.websocket_manager.broadcast_to_document(message, document_id)
    
    async def notify_document_analysis_progress(
        self, 
        document_id: str, 
        progress: int, 
        current_step: str = None
    ):
        """Notify about document analysis progress"""
        message = {
            "type": "document_analysis_progress",
            "document_id": document_id,
            "progress": progress,
            "current_step": current_step,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "analyzing"
        }
        
        await self.websocket_manager.notify_document_analysis_update(
            document_id, "in_progress", progress=progress
        )
        
        await self.websocket_manager.broadcast_to_document(message, document_id)
    
    async def notify_document_analysis_completed(
        self, 
        document_id: str, 
        analysis_results: Dict[str, Any],
        processing_time: float
    ):
        """Notify about completed document analysis"""
        # Prepare summary of results
        results_summary = {
            "overall_risk_score": float(analysis_results.get("overall_risk_score", 0)),
            "risk_level": analysis_results.get("risk_level", "unknown"),
            "confidence_score": float(analysis_results.get("confidence_score", 0)),
            "critical_issues_count": len(analysis_results.get("critical_issues", [])),
            "compliance_flags_count": len(analysis_results.get("compliance_flags", [])),
            "key_findings": analysis_results.get("key_findings", [])[:3],  # Top 3 findings
            "processing_time": processing_time
        }
        
        message = {
            "type": "document_analysis_completed",
            "document_id": document_id,
            "results_summary": results_summary,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "completed"
        }
        
        await self.websocket_manager.notify_document_analysis_update(
            document_id, "completed", progress=100, results=results_summary
        )
        
        await self.websocket_manager.broadcast_to_document(message, document_id)
    
    async def notify_document_analysis_failed(
        self, 
        document_id: str, 
        error_message: str
    ):
        """Notify about failed document analysis"""
        message = {
            "type": "document_analysis_failed",
            "document_id": document_id,
            "error_message": error_message,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "failed"
        }
        
        await self.websocket_manager.notify_document_analysis_update(
            document_id, "failed"
        )
        
        await self.websocket_manager.broadcast_to_document(message, document_id)
    
    async def notify_risk_assessment_started(
        self, 
        deal_id: str, 
        assessment_name: str,
        document_count: int
    ):
        """Notify about risk assessment start"""
        message = {
            "type": "risk_assessment_started",
            "deal_id": deal_id,
            "assessment_name": assessment_name,
            "document_count": document_count,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "assessing"
        }
        
        await self.websocket_manager.broadcast_to_deal(message, deal_id)
    
    async def notify_risk_assessment_completed(
        self, 
        deal_id: str, 
        assessment_results: Dict[str, Any]
    ):
        """Notify about completed risk assessment"""
        # Prepare summary
        results_summary = {
            "overall_risk_score": float(assessment_results.get("overall_risk_score", 0)),
            "risk_level": assessment_results.get("risk_level", "unknown"),
            "critical_issues": assessment_results.get("critical_issues", [])[:5],  # Top 5 issues
            "missing_documents_count": len(assessment_results.get("missing_documents", [])),
            "compliance_status": assessment_results.get("compliance_status", "unknown")
        }
        
        message = {
            "type": "risk_assessment_completed",
            "deal_id": deal_id,
            "results_summary": results_summary,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "completed"
        }
        
        await self.websocket_manager.notify_risk_assessment_update(
            deal_id, 
            "completed", 
            risk_score=results_summary["overall_risk_score"],
            critical_issues=[issue.get("description", "") for issue in results_summary["critical_issues"]]
        )
        
        await self.websocket_manager.broadcast_to_deal(message, deal_id)
    
    async def notify_compliance_alert(
        self, 
        document_id: str, 
        alert_type: str,
        severity: str,
        description: str,
        organization_id: str
    ):
        """Notify about compliance alerts"""
        message = {
            "type": "compliance_alert",
            "document_id": document_id,
            "alert_type": alert_type,
            "severity": severity,
            "description": description,
            "timestamp": datetime.utcnow().isoformat(),
            "requires_action": severity in ["high", "critical"]
        }
        
        # Send to document collaborators
        await self.websocket_manager.broadcast_to_document(message, document_id)
        
        # Also send to organization if high severity
        if severity in ["high", "critical"]:
            await self.websocket_manager.broadcast_to_organization(message, organization_id)
    
    async def notify_user_mention(
        self, 
        mentioned_user_id: str,
        mentioning_user_id: str,
        mentioning_user_name: str,
        document_id: str,
        context: str
    ):
        """Notify user about being mentioned in a document"""
        message = {
            "type": "user_mentioned",
            "document_id": document_id,
            "mentioned_by": {
                "user_id": mentioning_user_id,
                "user_name": mentioning_user_name
            },
            "context": context,
            "timestamp": datetime.utcnow().isoformat(),
            "action_required": True
        }
        
        await self.websocket_manager.send_personal_message(message, mentioned_user_id)
    
    async def notify_document_shared(
        self, 
        document_id: str,
        shared_with_user_id: str,
        shared_by_user_id: str,
        shared_by_user_name: str,
        permission_level: str
    ):
        """Notify user about document being shared with them"""
        message = {
            "type": "document_shared",
            "document_id": document_id,
            "shared_by": {
                "user_id": shared_by_user_id,
                "user_name": shared_by_user_name
            },
            "permission_level": permission_level,
            "timestamp": datetime.utcnow().isoformat(),
            "action_required": False
        }
        
        await self.websocket_manager.send_personal_message(message, shared_with_user_id)
    
    async def notify_system_maintenance(
        self, 
        maintenance_type: str,
        start_time: datetime,
        estimated_duration: int,
        organization_id: str = None
    ):
        """Notify about system maintenance"""
        message = {
            "type": "system_maintenance",
            "maintenance_type": maintenance_type,
            "start_time": start_time.isoformat(),
            "estimated_duration_minutes": estimated_duration,
            "timestamp": datetime.utcnow().isoformat(),
            "action_required": False
        }
        
        if organization_id:
            await self.websocket_manager.broadcast_to_organization(message, organization_id)
        else:
            # Broadcast to all organizations
            for org_id in self.websocket_manager.organization_rooms.keys():
                await self.websocket_manager.broadcast_to_organization(message, org_id)
    
    async def send_custom_notification(
        self, 
        notification_type: str,
        message_data: Dict[str, Any],
        target_type: str,  # "user", "document", "deal", "organization"
        target_id: str
    ):
        """Send custom notification to specific target"""
        message = {
            "type": notification_type,
            "timestamp": datetime.utcnow().isoformat(),
            **message_data
        }
        
        if target_type == "user":
            await self.websocket_manager.send_personal_message(message, target_id)
        elif target_type == "document":
            await self.websocket_manager.broadcast_to_document(message, target_id)
        elif target_type == "deal":
            await self.websocket_manager.broadcast_to_deal(message, target_id)
        elif target_type == "organization":
            await self.websocket_manager.broadcast_to_organization(message, target_id)


# Global notification service instance
realtime_notifications = RealtimeNotificationService()
